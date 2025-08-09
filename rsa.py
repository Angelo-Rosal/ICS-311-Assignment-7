from uuid import uuid4
from sharedDataStructure import Person, Message, Graph
import random 
import math

# RSA math functions

# modular exponentiation
def power(base, expo, m):
    res = 1
    base = base % m
    while expo > 0:
        if expo & 1:
            res = (res * base) % m
        base = (base * base) % m
        expo = expo // 2
    return res

# greatest common divisor
def gcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else: 
        g, y, x = gcd(b % a, a)
        return (g, x - (b // a) * y, y)

# modular inverse: finds d such that (d*e) % phi == 1
def modInverse(e, phi):
    g, x, y = gcd(e, phi)
    if g != 1:
        return None
    else:
        return x % phi
    
# miller rabin primality test iteration
def miller_rabin_test(d, n):
    a = random.randint(2, n - 2)
    x = pow(a, d, n)

    if x == 1 or x == n - 1:
        return True

    while d != n - 1:
        x = (x * x) % n
        d *= 2

        if x == 1:
            return False
        if x == n - 1:
            return True

    return False

# checks if n is prime
"""
# uses miller rabin primality test
n: number to test for primality
k: number of rounds (higher k = more accuracy)
returns true if n is probably prime, false if composite
"""
def isPrime(n, k=5):
    if n <= 1:
        return False
    if n <= 3:
        return True
    d = n - 1
    while d % 2 == 0:
        d //= 2

    for _ in range(k):
        if not miller_rabin_test(d, n):
            return False
    return True
# generate a random prime number to be used for key generation
def genRandPrime(min_val=1000, max_val=10000):
    while True:
        candidate = random.randint(min_val, max_val)
        # make sure candidate is odd
        if candidate % 2 == 0:
            candidate += 1
        if isPrime(candidate):
            return candidate

# generate RSA keys
def generateKeys():
    # two prime numbers
    p = genRandPrime()
    q = genRandPrime()
    while q == p:
        q = genRandPrime()
    n = p*q
    phi = (p - 1) * (q - 1)

    e = 65537
    if gcd(e, phi) != 1:
        # fallback to another e if required
        for candidate in range(2, phi):
            if gcd(candidate, phi) == 1:
                e = candidate
                break
    
    # find mod inverse of e
    d = modInverse(e, phi)
    if d is None:
        raise Exception("Failed to find modular inverse.")

    # public key, private key
    return e, d, n

"""
conversion helpers
"""
def text_to_int(text: str) -> int:
    return int.from_bytes(text.encode('utf-8'), byteorder='big')

def int_to_text(num: int) -> str:
    return num.to_bytes((num.bit_length() + 7) // 8, byteorder='big').decode('utf-8')

def tuple_to_bytes(t: tuple) -> bytes:
    """Store (e, n) or (d, n) as bytes."""
    return f"{t[0]},{t[1]}".encode('utf-8')

def bytes_to_tuple(b: bytes) -> tuple:
    parts = b.decode('utf-8').split(',')
    return int(parts[0]), int(parts[1])

"""
Messaging functions
"""

def setKeysForPerson(person: Person):
    e, d, n = generateKeys()
    public_key = (e, n)
    private_key = (d, n)
    person.public_key_pem = tuple_to_bytes(public_key)
    person.private_key_pem = tuple_to_bytes(private_key)

def rsaEncrypt(sender: Person, receiver: Person, plaintext: str) -> Message:
    if not receiver.public_key_pem:
        raise ValueError("Receiver has no public key.")
    
    e, n = bytes_to_tuple(receiver.public_key_pem)
    m_int = text_to_int(plaintext)
    c_int = power(m_int, e, n)
    c_bytes = str(c_int).encode('utf-8')

    msg = Message(
        id=str(uuid4()),
        sender_id=sender.id,
        receiver_id=receiver.id,
        body=c_bytes,
        metadata={"algorithm": "RSA-basic"}
    )
    sender.outbox.append(msg)
    return msg

def rsaDecrypt(receiver: Person, message: Message) -> str:
    if not receiver.private_key_pem:
        raise ValueError("Receiver has no private key.")

    d, n = bytes_to_tuple(receiver.private_key_pem)
    c_int = int(message.body.decode('utf-8'))
    m_int = power(c_int, d, n)
    plaintext = int_to_text(m_int)

    receiver.inbox.append(message)
    return plaintext


"""
Test
"""

if __name__ == "__main__":
    g = Graph()
    alice = g.add_person("Alice")
    bob = g.add_person("Bob")

    setKeysForPerson(alice)
    setKeysForPerson(bob)

    print("Alice's public key: ", alice.public_key_pem)
    print("Alice's private key: ", alice.private_key_pem)
    print("Bob's public key: ", bob.public_key_pem)
    print("Bob's private key: ", bob.private_key_pem)
    
    
    msg = "HI"
    print("original message: ", msg)

    # Alice sends Bob a message
    encryptedMsg = rsaEncrypt(alice, bob, msg)
    print("ciphertext: ", encryptedMsg.body)

    # Bob decrypts Alice's message
    plaintext = rsaDecrypt(bob, encryptedMsg)
    print("decrypted message: ", plaintext)