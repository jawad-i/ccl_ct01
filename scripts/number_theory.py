"""
Number Theory Foundations & Cryptographic Mathematics
Author: Md. Akib Al Jawad (IT-23020)
Department of Information and Communication Technology (ICT)
Mawlana Bhashani Science and Technology University (MBSTU)
"""

def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm.
    Returns (d, x, y) such that:
        d = gcd(a, b)
        a*x + b*y = d
    Requires: a >= b >= 0 and a + b > 0.
    """
    assert a >= b and b >= 0 and a + b > 0, "Preconditions violated: a >= b >= 0 and a + b > 0"
    
    if b == 0:
        d, x, y = a, 1, 0
    else:
        d, x1, y1 = extended_gcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        
    assert a % d == 0 and b % d == 0, "d does not divide a and b"
    assert d == a * x + b * y, "Bézout's identity check failed"
    return (d, x, y)


def gcd(a, b):
    """Standard Euclidean Algorithm for GCD."""
    while b:
        a, b = b, a % b
    return abs(a)


def lcm(a, b):
    """
    Computes Least Common Multiple of two positive integers.
    Uses the relation: lcm(a, b) = (a * b) // gcd(a, b)
    """
    assert a > 0 and b > 0, "Both integers must be positive"
    g = gcd(a, b)
    return (a * b) // g


def diophantine(a, b, c):
    """
    Solves the linear Diophantine equation: ax + by = c.
    Returns integers (x, y) satisfying the equation.
    Requires: a > 0, b > 0, and c % gcd(a, b) == 0.
    """
    assert a > 0 and b > 0, "Coefficients a and b must be positive"
    
    # Use extended_gcd respecting the a >= b condition
    if a >= b:
        d, x0, y0 = extended_gcd(a, b)
    else:
        d, y0, x0 = extended_gcd(b, a)
        
    gcd_val = d
    assert c % gcd_val == 0, f"No integer solution exists: gcd({a}, {b}) = {gcd_val} does not divide {c}"
    
    scale = c // gcd_val
    x = x0 * scale
    y = y0 * scale
    
    assert a * x + b * y == c, "Diophantine equation check failed"
    return (x, y)


def mod_inverse(a, n):
    """
    Calculates the multiplicative inverse of a modulo n.
    Finds integer x in [0, n - 1] such that (a * x) % n == 1.
    Requires: gcd(a, n) == 1 and n > 1.
    """
    assert n > 1, "Modulus n must be greater than 1"
    a = a % n
    assert a > 0, "a must be coprime to n (cannot be 0 mod n)"
    
    # Extended Euclidean algorithm on n and a (since n > a)
    d, yn, ya = extended_gcd(n, a)
    assert d == 1, f"Inverse does not exist: gcd({a}, {n}) = {d} != 1"
    
    inv = ya % n
    assert (a * inv) % n == 1, "Modular inverse verification failed"
    return inv


def divide(b, a, n):
    """
    Modular division: Computes x such that a * x = b (mod n).
    Requires: gcd(a, n) == 1 and n > 1.
    """
    assert n > 1 and a > 0, "n > 1 and a > 0 required"
    a_inv = mod_inverse(a, n)
    assert (a * a_inv) % n == 1
    return (a_inv * b) % n


def fast_modular_exponentiation(b, e, m):
    """
    Fast Modular Exponentiation using Square-and-Multiply.
    Computes (b^e) mod m in O(log e) operations without built-in pow(b, e, m).
    """
    assert m > 0, "Modulus must be positive"
    if m == 1:
        return 0
    
    res = 1
    base = b % m
    exp = e
    
    while exp > 0:
        if exp % 2 == 1:
            res = (res * base) % m
        base = (base * base) % m
        exp //= 2
        
    return res


def chinese_remainder_theorem(n1, r1, n2, r2):
    """
    Constructs r such that:
        r = r1 (mod n1)
        r = r2 (mod n2)
        0 <= r < n1 * n2
    Requires: gcd(n1, n2) == 1 and n1 > n2.
    """
    d, x, y = extended_gcd(n1, n2)
    assert d == 1, f"Moduli must be coprime, got gcd({n1}, {n2}) = {d}"
    
    # n1*x + n2*y = 1
    # Hence: n2*y = 1 (mod n1) and n2*y = 0 (mod n2)
    #        n1*x = 0 (mod n1) and n1*x = 1 (mod n2)
    # Solution: r = r1 * n2 * y + r2 * n1 * x
    modulus = n1 * n2
    r = (r1 * n2 * y + r2 * n1 * x) % modulus
    return (r + modulus) % modulus


def int_sqrt(n):
    """
    Computes floor(sqrt(n)) using integer binary search.
    Handles arbitrarily large integers safely.
    """
    assert n >= 0, "Cannot compute square root of negative integer"
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


def repunit_analysis(p):
    """
    Analyzes divisibility of the repunit sequence a(n) = (10^n - 1) / 9 by prime p.
    Returns:
        is_empty: True if A_p is empty, False otherwise.
        period: Minimal n > 0 such that p divides a(n).
    """
    if p in (2, 3, 5):
        if p == 2:
            # a(n) always ends in 1, always odd -> never divisible by 2
            return True, None
        elif p == 5:
            # a(n) ends in 1, never 0 or 5 -> never divisible by 5
            return True, None
        elif p == 3:
            # 3 | a(n) iff n is a multiple of 3 (sum of digits = n)
            return False, 3
    
    # For p != 2, 3, 5:
    # p | a(n) <=> 10^n = 1 (mod 9p)
    # Since gcd(10, 9p) = 1, by Euler's Totient Theorem, 10^phi(9p) = 1 (mod 9p).
    # Thus, an infinite set exists: n is any multiple of ord_{9p}(10).
    target_mod = 9 * p
    cur = 10 % target_mod
    n = 1
    while cur != 1 and n <= target_mod:
        cur = (cur * 10) % target_mod
        n += 1
    return False, n


if __name__ == "__main__":
    print("[*] Running Number Theory Foundations Unit Tests...")
    # Test Extended GCD
    d, x, y = extended_gcd(8, 4)
    assert (d, x, y) == (4, 0, 1) or 8*x + 4*y == 4
    d, x, y = extended_gcd(27, 15)
    assert d == 3 and 27*x + 15*y == 3
    print("    [+] Extended GCD: PASS")
    
    # Test LCM
    assert lcm(9, 3) == 9
    assert lcm(17, 37) == 629
    print("    [+] LCM: PASS")
    
    # Test Diophantine
    x, y = diophantine(34, 51, 170)
    assert 34 * x + 51 * y == 170
    x, y = diophantine(91, 117, 65)
    assert 91 * x + 117 * y == 65
    print("    [+] Diophantine: PASS")
    
    # Test Modular Inverse & Division
    assert mod_inverse(3, 7) == 5
    assert divide(9, 5, 3) == 0
    assert divide(223, 67, 54) == 13
    print("    [+] Modular Inverse & Division: PASS")
    
    # Test Fast Exponentiation
    assert fast_modular_exponentiation(4, 5, 3) == pow(4, 5, 3)
    assert fast_modular_exponentiation(7, 256, 13) == pow(7, 256, 13)
    print("    [+] Fast Modular Exponentiation: PASS")
    
    # Test CRT
    assert chinese_remainder_theorem(13, 7, 6, 5) == 59
    assert chinese_remainder_theorem(28, 20, 19, 3) == 440
    print("    [+] Chinese Remainder Theorem: PASS")
    
    # Test Repunit divisibility
    empty_2, _ = repunit_analysis(2)
    empty_5, _ = repunit_analysis(5)
    empty_7, period_7 = repunit_analysis(7)
    assert empty_2 and empty_5 and not empty_7 and period_7 == 6
    print("    [+] Repunit Analysis: PASS")
    print("[+] All Number Theory tests passed successfully!\n")
