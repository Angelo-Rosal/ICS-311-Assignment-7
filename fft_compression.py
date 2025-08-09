from __future__ import annotations
import numpy as np
from uuid import uuid4
from sharedDataStructure import Person, Message, Graph

# function for sending message with FFT compression
def send_message(self, sender_id: str, receiver_id: str, text: str, compression_ratio: float = 0.5):
        compressed_text = lossy_fft_compress(text, compression_ratio).encode("utf-8")
        metadata = {  # metadata
            "original_length": len(text),
            "compression_ratio": compression_ratio,
            "method": "lossy_fft"
        }
        msg = Message(id=str(uuid4()), sender_id=sender_id, receiver_id=receiver_id, body=compressed_text, metadata=metadata)
        self.people[sender_id].outbox.append(msg)
        self.people[receiver_id].inbox.append(msg)
        return msg

Graph.send_message = send_message 

# perform lossy FFT compression on a given string
def lossy_fft_compress(text: str, keep_ratio: float = 0.5) -> str:
    # convert text to numeric/frequency representation
    numeric = np.array([ord(c) for c in text], dtype=float)
    freq = np.fft.fft(numeric)

    # apply FFT
    cutoff = int(len(freq) * keep_ratio)
    filtered = np.zeros_like(freq)
    filtered[:cutoff] = freq[:cutoff]

    # apply inverse FFT
    approx_numeric = np.fft.ifft(filtered).real

    # convert back to text, staying within valid Unicode range
    approx_text = ''.join(chr(int(max(0, min(round(x), 1114111)))) for x in approx_numeric)
    return approx_text

# create graph and users
g = Graph()
alice = g.add_person("Alice")
john = g.add_person("John")
text = "Hello John, how are you? This is a test message to demonstrate lossy FFT compression."

# send lossy compressed message
msg = g.send_message(alice.id, john.id, text, compression_ratio=0.3)

# print results
print("Sent Message:", text)
print("Compressed message (bytes):", msg.body)
print("Metadata:", msg.metadata)