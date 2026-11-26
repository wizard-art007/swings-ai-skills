import sys
sys.path.insert(0, "src")

from heuristics import (
    egcd,
    mod_inverse,
    is_prime,
    pollard_rho_factor,
    factorize,
    baby_step_giant_step,
    pollard_rho_dlog,
)


def test_egcd_and_mod_inverse():
    g, x, y = egcd(30, 20)
    assert g == 10 and 30 * x + 20 * y == 10
    assert mod_inverse(3, 11) == 4
    assert mod_inverse(6, 9) is None


def test_primality_and_factorization():
    assert is_prime(2) and is_prime(1019) and not is_prime(1020)
    p = pollard_rho_factor(8051)
    assert p in (83, 97)
    assert factorize(360) == [2, 2, 2, 3, 3, 5]
    assert factorize(8051) == [83, 97]


def test_baby_step_giant_step():
    p, g, x = 1019, 2, 733
    h = pow(g, x, p)
    assert baby_step_giant_step(g, h, p, order=p - 1) == x


def test_pollard_rho_dlog():
    p = 1019  # safe prime: (p-1)/2 = 509 is prime
    g = 2     # primitive root modulo p
    expected_x = 733
    h = pow(g, expected_x, p)
    found_x = pollard_rho_dlog(g, h, p, order=p - 1)
    assert found_x is not None
    assert pow(g, found_x, p) == h


def test_edge_cases():
    assert factorize(1) == []
    p, g = 997, 7
    assert baby_step_giant_step(g, 1, p) == 0
    assert pollard_rho_dlog(g, 1, p) == 0
    assert baby_step_giant_step(g, g, p) == 1
    assert pollard_rho_dlog(g, g, p) == 1
