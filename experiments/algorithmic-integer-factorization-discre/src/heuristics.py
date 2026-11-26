import math
import random


def egcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclidean algorithm: returns (g, x, y) such that a*x + b*y = g."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a: int, m: int) -> int | None:
    g, x, _ = egcd(a, m)
    return (x % m + m) % m if g == 1 else None


def pollard_rho_factor(n: int, max_steps: int = 100000) -> int | None:
    """Find a non-trivial factor of composite n using Pollard's rho algorithm."""
    if n % 2 == 0:
        return 2
    for c in (1, 3, 5, 7):
        f = lambda x: (x * x + c) % n
        x, y, d = 2, 2, 1
        steps = 0
        while d == 1 and steps < max_steps:
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x - y), n)
            steps += 1
        if 1 < d < n:
            return d
    return None


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 7, 61):
        if a >= n:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def factorize(n: int) -> list[int]:
    """Fully factorize an integer n into sorted prime factors."""
    if n <= 1:
        return []
    factors = []
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    stack = [n] if n > 1 else []
    while stack:
        curr = stack.pop()
        if is_prime(curr):
            factors.append(curr)
        else:
            divisor = pollard_rho_factor(curr)
            if divisor is None or divisor == curr:
                # Small trial division fallback
                for i in range(3, int(math.isqrt(curr)) + 1, 2):
                    if curr % i == 0:
                        divisor = i
                        break
                else:
                    divisor = curr
            stack.append(divisor)
            stack.append(curr // divisor)
    return sorted(factors)


def baby_step_giant_step(g: int, h: int, p: int, order: int | None = None) -> int | None:
    """Solve g^x = h (mod p) using Shank's Baby-step Giant-step."""
    h %= p
    if h == 1:
        return 0
    n = order or (p - 1)
    m = math.isqrt(n) + 1
    table = {}
    cur = 1
    for j in range(m):
        table[cur] = j
        cur = (cur * g) % p
    factor = mod_inverse(pow(g, m, p), p)
    if factor is None:
        return None
    gamma = h
    for i in range(m):
        if gamma in table:
            ans = i * m + table[gamma]
            if pow(g, ans, p) == h:
                return ans
        gamma = (gamma * factor) % p
    return None


def _rho_step(x: int, a: int, b: int, g: int, h: int, p: int, order: int) -> tuple[int, int, int]:
    mod3 = x % 3
    if mod3 == 0:
        return (x * x) % p, (2 * a) % order, (2 * b) % order
    if mod3 == 1:
        return (x * g) % p, (a + 1) % order, b
    return (x * h) % p, a, (b + 1) % order


def pollard_rho_dlog(
    g: int, h: int, p: int, order: int | None = None, max_steps: int = 50000
) -> int | None:
    """Solve g^x = h (mod p) using Pollard's rho algorithm for discrete log."""
    h %= p
    if h == 1:
        return 0
    if h == g % p:
        return 1
    N = order or (p - 1)
    rng = random.Random(42)

    for _ in range(30):
        a_t = rng.randint(0, N - 1)
        b_t = rng.randint(0, N - 1)
        x_t = (pow(g, a_t, p) * pow(h, b_t, p)) % p
        x_h, a_h, b_h = x_t, a_t, b_t

        for _ in range(max_steps):
            x_t, a_t, b_t = _rho_step(x_t, a_t, b_t, g, h, p, N)
            x_h, a_h, b_h = _rho_step(x_h, a_h, b_h, g, h, p, N)
            x_h, a_h, b_h = _rho_step(x_h, a_h, b_h, g, h, p, N)

            if x_t == x_h:
                r = (b_t - b_h) % N
                s = (a_h - a_t) % N
                d, u, _ = egcd(r, N)
                if s % d == 0:
                    base_sol = ((s // d) * mod_inverse(r // d, N // d)) % (N // d)
                    step = N // d
                    for k in range(d):
                        sol = (base_sol + k * step) % N
                        if pow(g, sol, p) == h:
                            return sol
                break
    return None
