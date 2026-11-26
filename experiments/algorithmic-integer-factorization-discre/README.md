# Algorithmic Integer Factorization & Discrete Log Experiment

A lightweight algebraic computation package demonstrating classical heuristics for integer factorization and cyclic-group discrete logarithm problems.

## Algorithms Implemented

1. **Pollard's $\rho$ Integer Factorization**:
   - Uses pseudo-random polynomial iterations $f(x) = x^2 + c \pmod n$ to detect non-trivial cycle collisions via $\gcd(|x - y|, n)$.
2. **Baby-step Giant-step (BSGS)**:
   - A deterministic space-time tradeoff algorithm running in $\mathcal{O}(\sqrt{N})$ group operations to solve $g^x \equiv h \pmod p$.
3. **Pollard's $\rho$ Discrete Logarithm**:
   - Group partition-based random walk utilizing Floyd's cycle finding to extract linear modular relations $(\beta_h - \beta_t) x \equiv (\alpha_t - \alpha_h) \pmod N$ with multiple randomized restarts and linear congruence solving.

## Running Tests

Run offline tests using pytest:

