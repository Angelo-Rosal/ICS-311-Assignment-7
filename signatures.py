from typing import Dict, Any
import base 64
from messeging import Message, Graph, s2b, b2x, sha256
from uuid import uuid4

SINGED_METHOD = "RSA-SIGN"
ACK_METHOD = "ACK"

def build_signed_message(sender_id: str, receiver_id: str, body_str: str, g: Graph) -> Message:
    """Create a signed message (not encrypted)."""
    sender = g.get(sender_id)
    raw = s2b(body_str)
    h = sha256(raw)
    sig = rsa_sign(h, sender.private_key_pem)
    meta: Dict[str, Any] = {
        "method": SIGNED_METHOD,
        "hash_alg": "SHA-256",
        "message_hash_hex": h.hex(),
        "signature_b64": base64.b64encode(sig).decode(),
        # optional but nice-to-have:
        "timestamp_iso": __now_iso(),
        "nonce": str(uuid4())
    }
    return Message(id=str(uuid4()), sender_id=sender_id, receiver_id=receiver_id, body=raw, metadata=meta)

def verify_signed_message(msg: Message, g: Graph) -> bool:
    """Return True if signature is valid for msg.body."""
    if msg.metadata.get("method") != SIGNED_METHOD:
        return False
    sender = g.get(msg.sender_id)
    # recompute and compare hash
    h_recv = sha256(msg.body)
    if h_recv.hex() != msg.metadata.get("message_hash_hex"):
        return False
    sig = base64.b64decode(msg.metadata["signature_b64"])
    return rsa_verify(h_recv, sig, sender.public_key_pem)

def build_signed_ack(received_msg: Message, receiver_id: str, g: Graph, valid: bool) -> Message:
    """Create a signed ACK that references the original signed message."""
    receiver = g.get(receiver_id)
    # ACK body can include human-readable status
    ack_body = s2b(f"ACK: valid={valid}")
    ack_hash = sha256(ack_body)
    ack_sig = rsa_sign(ack_hash, receiver.private_key_pem)

    ack_meta = {
        "method": ACK_METHOD,
        "orig_signature_b64": received_msg.metadata["signature_b64"],
        "orig_hash_hex": received_msg.metadata["message_hash_hex"],
        "ack_hash_hex": ack_hash.hex(),
        "ack_signature_b64": base64.b64encode(ack_sig).decode(),
        "timestamp_iso": __now_iso(),
        "nonce": str(uuid4())
    }
    return Message(
        id=str(uuid4()),
        sender_id=receiver_id,
        receiver_id=received_msg.sender_id,
        body=ack_body,
        metadata=ack_meta
    )

def __now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()