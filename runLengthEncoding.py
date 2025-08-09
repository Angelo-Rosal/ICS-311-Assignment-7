from uuid import uuid4
from sharedDataStructure import Graph, Message

METHOD_RLE = "rle"
CHARSET = "utf-8"

def _rle_encode_bytes(raw: bytes) -> bytes:
    """Encode bytes with classic run-length encoding -> ASCII like b'3a4b2c'."""
    if not raw:
        return b""
    out = bytearray()
    prev = raw[0]
    count = 1
    for b in raw[1:]:
        if b == prev and count < 10**9:
            count += 1
        else:
            out.extend(str(count).encode("ascii"))
            out.append(prev)
            prev = b
            count = 1
    out.extend(str(count).encode("ascii"))
    out.append(prev)
    return bytes(out)

def _rle_decode_bytes(data: bytes) -> bytes:
    """Inverse of _rle_encode_bytes."""
    if not data:
        return b""
    out = bytearray()
    digits = bytearray()
    for b in data:
        if 48 <= b <= 57:  # '0'..'9'
            digits.append(b)
        else:
            n = int(digits.decode("ascii")) if digits else 1
            out.extend([b] * n)
            digits.clear()
    return bytes(out)

def send_rle(g: Graph, sender_id: str, receiver_id: str, plaintext: str) -> Message:
    """
    Compresses plaintext with RLE, posts to receiver's inbox and sender's outbox,
    and returns the Message. Metadata marks the encoding.
    """
    encoded_body = _rle_encode_bytes(plaintext.encode(CHARSET))
    msg = Message(
        id = str(uuid4()),
        sender_id = sender_id,
        receiver_id = receiver_id,
        body = encoded_body,
        metadata = {"encoding": METHOD_RLE, "charset": CHARSET},
    )
    g.get(sender_id).outbox.append(msg)
    g.get(receiver_id).inbox.append(msg)
    return msg

def recv_rle(msg: Message) -> str:
    """
    Decodes an RLE-compressed message body back to a string.
    """
    assert msg.metadata.get("encoding") == METHOD_RLE, "Message is not RLE-encoded"
    raw = _rle_decode_bytes(msg.body)
    return raw.decode(msg.metadata.get("charset", CHARSET))
