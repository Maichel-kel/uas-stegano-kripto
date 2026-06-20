import os, base64, hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend

# Caesar
def caesar_encrypt(plaintext, shift):
    result = []
    for ch in plaintext:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return ''.join(result)

def caesar_decrypt(ciphertext, shift):
    return caesar_encrypt(ciphertext, -shift)

def caesar_bruteforce(ciphertext):
    return [(s, caesar_decrypt(ciphertext, s)) for s in range(1, 26)]

# Vigenere
def vigenere_encrypt(plaintext, key):
    key = key.upper(); result = []; ki = 0
    for ch in plaintext:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            k = ord(key[ki % len(key)]) - ord('A')
            result.append(chr((ord(ch) - base + k) % 26 + base)); ki += 1
        else:
            result.append(ch)
    return ''.join(result)

def vigenere_decrypt(ciphertext, key):
    key = key.upper(); result = []; ki = 0
    for ch in ciphertext:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            k = ord(key[ki % len(key)]) - ord('A')
            result.append(chr((ord(ch) - base - k) % 26 + base)); ki += 1
        else:
            result.append(ch)
    return ''.join(result)

# Affine
AFFINE_VALID_A = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]

def _mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1: return x
    raise ValueError(f"No inverse for a={a}")

def affine_encrypt(plaintext, a, b):
    result = []
    for ch in plaintext:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((a * (ord(ch) - base) + b) % 26 + base))
        else:
            result.append(ch)
    return ''.join(result)

def affine_decrypt(ciphertext, a, b):
    a_inv = _mod_inverse(a, 26); result = []
    for ch in ciphertext:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((a_inv * (ord(ch) - base - b)) % 26 + base))
        else:
            result.append(ch)
    return ''.join(result)

# AES-256 CBC
def _derive_key(password):
    return hashlib.sha256(password.encode()).digest()

def aes_encrypt(plaintext, password):
    key = _derive_key(password); iv = os.urandom(16)
    padder = sym_padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    ct = cipher.encryptor().update(padded) + cipher.encryptor().finalize()
    enc = cipher.encryptor()
    ct = enc.update(padded) + enc.finalize()
    return base64.b64encode(iv + ct).decode()

def aes_decrypt(ciphertext_b64, password):
    key = _derive_key(password)
    raw = base64.b64decode(ciphertext_b64)
    iv, ct = raw[:16], raw[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    dec = cipher.decryptor()
    padded = dec.update(ct) + dec.finalize()
    unpadder = sym_padding.PKCS7(128).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode()