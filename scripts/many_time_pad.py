"""
Many-Time Pad & Information-Theoretic Cryptanalysis
Author: Md. Akib Al Jawad (IT-23020)
Department of Information and Communication Technology (ICT)
Mawlana Bhashani Science and Technology University (MBSTU)
"""

import string
from collections import Counter


def to_hex(s: str) -> str:
    """Converts an ASCII string to a hex-encoded string."""
    return "".join(hex(ord(ch))[2:].zfill(2) for ch in s)


def from_hex(hex_str: str) -> str:
    """Converts a hex-encoded string back to ASCII."""
    bytes_list = [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]
    return "".join(chr(b) for b in bytes_list)


def xor_hex(hex_s1: str, hex_s2: str) -> str:
    """
    Computes XOR of two hex-encoded byte strings.
    hex_s1 and hex_s2 must have equal length.
    """
    assert len(hex_s1) == len(hex_s2), "Hex strings must have identical lengths"
    res = []
    for i in range(0, len(hex_s1), 2):
        b1 = int(hex_s1[i:i+2], 16)
        b2 = int(hex_s2[i:i+2], 16)
        res.append(hex(b1 ^ b2)[2:].zfill(2))
    return "".join(res)


def otp_encrypt(plaintext: str, key: str) -> str:
    """
    One-Time Pad encryption: C = M XOR K.
    Returns ciphertext as hex string.
    """
    assert len(plaintext) == len(key), "Key length must match message length"
    return xor_hex(to_hex(plaintext), to_hex(key))


def otp_decrypt(ciphertext_hex: str, key: str) -> str:
    """
    One-Time Pad decryption: M = C XOR K.
    Returns recovered plaintext string.
    """
    key_hex = to_hex(key)
    return from_hex(xor_hex(ciphertext_hex, key_hex))


def is_mostly_printable(text: str, threshold: float = 0.85) -> bool:
    """Checks whether the decoded string contains mostly printable ASCII characters."""
    if not text:
        return False
    printable_count = sum(1 for ch in text if ch in string.printable and ch not in '\r\x0b\x0c')
    return (printable_count / len(text)) >= threshold


def crib_drag(xor_ciphertexts_hex: str, crib: str):
    """
    Performs crib dragging against the XOR sum of two ciphertexts: C1 ^ C2 = M1 ^ M2.
    When a crib matches message 1, C1 ^ C2 ^ crib reveals the corresponding fragment of message 2.
    
    Returns a list of candidate matches: (position, revealed_text).
    """
    xor_bytes = [int(xor_ciphertexts_hex[i:i+2], 16) for i in range(0, len(xor_ciphertexts_hex), 2)]
    crib_bytes = [ord(c) for c in crib]
    crib_len = len(crib_bytes)
    total_len = len(xor_bytes)
    
    candidates = []
    for pos in range(total_len - crib_len + 1):
        revealed = []
        for j in range(crib_len):
            revealed.append(chr(xor_bytes[pos + j] ^ crib_bytes[j]))
        revealed_str = "".join(revealed)
        
        # Check if the revealed fragment contains readable English letters or spaces
        if all(ch.isalnum() or ch in " ,.'-;:!?" for ch in revealed_str):
            candidates.append((pos, revealed_str))
            
    return candidates


def caesar_cipher_encrypt(text: str, shift: int) -> str:
    """Encrypts text using Caesar shift cipher."""
    res = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            res.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            res.append(ch)
    return "".join(res)


def letter_frequency_analysis(text: str):
    """Calculates English letter frequencies in given ciphertext."""
    filtered = [ch.upper() for ch in text if ch.isalpha()]
    total = len(filtered)
    if total == 0:
        return {}
    counts = Counter(filtered)
    return {k: round((v / total) * 100, 2) for k, v in sorted(counts.items())}


if __name__ == "__main__":
    print("[*] Running Many-Time Pad & Information Theory Unit Tests...")
    m1 = "steal the secret"
    m2 = "the cat the bird"
    key = "supersecretverys"
    
    # 1. OTP Encryption & Decryption
    c1 = otp_encrypt(m1, key)
    c2 = otp_encrypt(m2, key)
    assert otp_decrypt(c1, key) == m1
    assert otp_decrypt(c2, key) == m2
    print("    [+] One-Time Pad Correctness: PASS")
    
    # 2. Many-Time Pad Vulnerability Demo (C1 ^ C2 = M1 ^ M2)
    c_xor = xor_hex(c1, c2)
    m_xor = xor_hex(to_hex(m1), to_hex(m2))
    assert c_xor == m_xor, "C1 ^ C2 must equal M1 ^ M2"
    print("    [+] Two-Time Pad Key Cancellation: PASS")
    
    # 3. Crib Dragging Test
    # If Eve drags crib 'the ', it should match parts of m1 or m2
    matches = crib_drag(c_xor, "the ")
    assert len(matches) > 0
    print(f"    [+] Crib Dragging matched candidates: {matches}")
    
    # 4. Caesar Cipher test
    caesar_ct = caesar_cipher_encrypt("ATTACK AT DAWN", 3)
    assert caesar_ct == "DWWDFN DW GDZQ"
    print("    [+] Caesar Cipher: PASS")
    
    freq = letter_frequency_analysis(caesar_ct)
    print(f"    [+] Frequency analysis sample: {freq}")
    print("[+] All Many-Time Pad tests passed successfully!\n")
