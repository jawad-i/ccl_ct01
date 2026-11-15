"""
RSA Cryptosystem & Cryptanalytic Vulnerabilities
Author: Md. Akib Al Jawad (IT-23020)
Department of Information and Communication Technology (ICT)
Mawlana Bhashani Science and Technology University (MBSTU)

Comprehensive implementations of RSA primitives and standard cryptanalytic attacks:
1. Basic RSA Encryption & Decryption
2. Small Message Space Dictionary Attack (Precomputation)
3. Small Prime Factorization (Trial Division)
4. Fermat's Factorization for Close Primes (|p - q| < Bound)
5. Shared Factor / Common Modulus GCD Attack (Batch GCD)
6. Håstad's Broadcast Attack for Small Public Exponent (e = 2) via CRT
"""

import math


def ConvertToInt(message_str: str) -> int:
    """Converts an ASCII text string to a big integer in base-256."""
    res = 0
    for ch in message_str:
        res = res * 256 + ord(ch)
    return res


def ConvertToStr(n: int) -> str:
    """Converts a big integer back to an ASCII string."""
    res = []
    while n > 0:
        res.append(chr(n % 256))
        n //= 256
    return "".join(reversed(res))


def PowMod(a: int, n: int, mod: int) -> int:
    """Computes (a^n) mod mod using fast modular exponentiation."""
    return pow(a, n, mod)


def ExtendedEuclid(a: int, b: int):
    """
    Extended Euclidean Algorithm.
    Returns (x, y) such that a*x + b*y = gcd(a, b).
    """
    if b == 0:
        return (1, 0)
    (x1, y1) = ExtendedEuclid(b, a % b)
    k = a // b
    return (y1, x1 - k * y1)


def InvertModulo(a: int, n: int) -> int:
    """
    Computes multiplicative inverse of a modulo n.
    Returns integer b such that (a * b) % n == 1.
    """
    (b, _) = ExtendedEuclid(a, n)
    b = (b % n + n) % n
    return b


def Encrypt(message: str, modulo: int, exponent: int) -> int:
    """
    RSA Public-Key Encryption.
    c = m^e (mod N)
    """
    m = ConvertToInt(message)
    return PowMod(m, exponent, modulo)


def Decrypt(ciphertext: int, p: int, q: int, exponent: int) -> str:
    """
    RSA Private-Key Decryption.
    m = c^d (mod N), where d = e^(-1) mod phi(N)
    """
    phi = (p - 1) * (q - 1)
    d = InvertModulo(exponent, phi)
    n = p * q
    m = PowMod(ciphertext, d, n)
    return ConvertToStr(m)


# --------------------------------------------------------------------------
# Cryptanalytic Attacks on RSA
# --------------------------------------------------------------------------

def DecipherSimple(ciphertext: int, modulo: int, exponent: int, potential_messages: list) -> str:
    """
    Attack 1: Small Message Space Dictionary Attack.
    When plaintext is selected from a small predictable set without randomized padding,
    the attacker encrypts every potential candidate until matching the intercepted ciphertext.
    """
    for msg in potential_messages:
        if Encrypt(msg, modulo, exponent) == ciphertext:
            return msg
    return "don't know"


def DecipherSmallPrime(ciphertext: int, modulo: int, exponent: int, limit: int = 1000000) -> str:
    """
    Attack 2: Small Prime Factorization.
    If one prime factor p is small (e.g. p < 1,000,000), trial division easily
    recovers p and q = N // p, allowing full private key reconstruction.
    """
    for p in range(2, limit + 1):
        if modulo % p == 0:
            q = modulo // p
            return Decrypt(ciphertext, p, q, exponent)
    return "don't know"


def IntSqrt(n: int) -> int:
    """Computes floor(sqrt(n)) using binary search for arbitrary size integers."""
    if n < 0:
        raise ValueError("Cannot take square root of negative integer")
    if n == 0 or n == 1:
        return n
    low = 1
    high = n
    while low < high:
        mid = (low + high + 1) // 2
        if mid * mid <= n:
            low = mid
        else:
            high = mid - 1
    return low


def DecipherSmallDiff(ciphertext: int, modulo: int, exponent: int, max_steps: int = 50000) -> str:
    """
    Attack 3: Fermat Factorization for Close Primes.
    If |p - q| is small, N can be factored by testing a = ceil(sqrt(N)) + k,
    evaluating b^2 = a^2 - N until b^2 is a perfect square.
    Then p = a - b and q = a + b.
    """
    s = IntSqrt(modulo)
    for a in range(s, s + max_steps):
        b2 = a * a - modulo
        if b2 >= 0:
            b = IntSqrt(b2)
            if b * b == b2:
                p = a - b
                q = a + b
                if p * q == modulo and p > 1:
                    return Decrypt(ciphertext, p, q, exponent)
    return "don't know"


def GCD(a: int, b: int) -> int:
    """Iterative Euclidean algorithm for greatest common divisor."""
    while b:
        a, b = b, a % b
    return abs(a)


def DecipherCommonDivisor(first_ciphertext: int, first_modulo: int, first_exponent: int,
                           second_ciphertext: int, second_modulo: int, second_exponent: int):
    """
    Attack 4: Shared Factor / Common Modulus GCD Attack.
    When two public keys share a prime factor (e.g., due to insufficient PRNG entropy),
    gcd(N1, N2) = p instantly reveals the private factors:
        q1 = N1 // p,  q2 = N2 // p.
    Both ciphertexts are immediately decrypted.
    """
    common_p = GCD(first_modulo, second_modulo)
    assert common_p > 1, "Moduli do not share a common factor"
    q1 = first_modulo // common_p
    q2 = second_modulo // common_p
    m1 = Decrypt(first_ciphertext, common_p, q1, first_exponent)
    m2 = Decrypt(second_ciphertext, common_p, q2, second_exponent)
    return (m1, m2)


def ChineseRemainderTheorem(n1: int, r1: int, n2: int, r2: int) -> int:
    """
    Solves system:
        x = r1 (mod n1)
        x = r2 (mod n2)
    where gcd(n1, n2) == 1.
    """
    (x, y) = ExtendedEuclid(n1, n2)
    modulus = n1 * n2
    r = (r1 * n2 * y + r2 * n1 * x) % modulus
    return (r + modulus) % modulus


def DecipherHastad(first_ciphertext: int, first_modulo: int,
                   second_ciphertext: int, second_modulo: int) -> str:
    """
    Attack 5: Håstad's Broadcast Attack for small exponent e = 2.
    When the same message m is sent to 2 recipients with public exponent e = 2:
        c1 = m^2 mod N1
        c2 = m^2 mod N2
    Using CRT, we find c = m^2 mod (N1 * N2).
    Since m < min(N1, N2), m^2 < N1 * N2, so c is the exact integer square of m!
    Taking m = floor(sqrt(c)) recovers the plaintext without factoring.
    """
    c = ChineseRemainderTheorem(first_modulo, first_ciphertext, second_modulo, second_ciphertext)
    m = IntSqrt(c)
    assert m * m == c, "Resulting value is not a perfect square"
    return ConvertToStr(m)


if __name__ == "__main__":
    print("[*] Running RSA & Cryptanalysis Unit Tests...")
    
    # 1. Basic RSA
    p = 1000000007
    q = 1000000009
    exponent = 23917
    modulo = p * q
    ct = Encrypt("attack", modulo, exponent)
    pt = Decrypt(ct, p, q, exponent)
    assert pt == "attack"
    print("    [+] Basic RSA Encrypt/Decrypt: PASS")
    
    # 2. Dictionary attack
    recovered = DecipherSimple(ct, modulo, exponent, ["attack", "don't attack", "wait"])
    assert recovered == "attack"
    print("    [+] Attack 1 (Dictionary Attack): PASS")
    
    # 3. Small prime attack
    small_p = 101
    large_q = 18298970732541109011012304219376080251334480295537316123696052970419466495220522723330315111017831737980079504337868198011077274303193766040393009648852841770668239779097280026631944319501437547002412556176186750790476901358334138818777298389724049250700606462316428106882097210008142941838672676714188593227684360287806974345181893018133710957167334490627178666071809992955566020058374505477745993383434501768887090900283569055646901291270870833498474402084748161755197005050874785474707550376333429671113753137201128897550014524209754619355308207537703754006699795711188492048286436285518105948050401762394690148387
    small_mod = small_p * large_q
    small_e = 239
    ct_sp = Encrypt("attack", small_mod, small_e)
    pt_sp = DecipherSmallPrime(ct_sp, small_mod, small_e)
    assert pt_sp == "attack"
    print("    [+] Attack 2 (Small Prime Factorization): PASS")
    
    # 4. Small diff attack
    p_diff = 1000000007
    q_diff = 1000000009
    n_diff = p_diff * q_diff
    e_diff = 239
    ct_sd = Encrypt("attack", n_diff, e_diff)
    pt_sd = DecipherSmallDiff(ct_sd, n_diff, e_diff)
    assert pt_sd == "attack"
    print("    [+] Attack 3 (Fermat Factorization): PASS")
    
    # 5. Shared Divisor attack
    n1_cd = 101 * large_q
    n2_cd = 101 * 1000000007
    c1_cd = Encrypt("attack", n1_cd, 239)
    c2_cd = Encrypt("wait", n2_cd, 17)
    res_cd = DecipherCommonDivisor(c1_cd, n1_cd, 239, c2_cd, n2_cd, 17)
    assert res_cd == ("attack", "wait")
    print("    [+] Attack 4 (Shared Modulus GCD): PASS")
    
    # 6. Hastad Broadcast attack
    p1_h = 790383132652258876190399065097
    q1_h = 662503581792812531719955475509
    p2_h = 656917682542437675078478868539
    q2_h = 1263581691331332127259083713503
    n1_h = p1_h * q1_h
    n2_h = p2_h * q2_h
    c1_h = Encrypt("attack", n1_h, 2)
    c2_h = Encrypt("attack", n2_h, 2)
    pt_h = DecipherHastad(c1_h, n1_h, c2_h, n2_h)
    assert pt_h == "attack"
    print("    [+] Attack 5 (Håstad Broadcast Attack): PASS")
    
    print("[+] All RSA Cryptanalysis tests passed successfully!\n")
