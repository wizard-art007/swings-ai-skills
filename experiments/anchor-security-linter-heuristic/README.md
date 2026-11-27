# Anchor Security Linter Heuristic (AnchorSecLint)

A lightweight, offline heuristic security linter for Solana Anchor smart contracts written in Python 3.

## Idea & Motivation
Solana smart contracts built with the Anchor framework rely heavily on macro annotations (`#[account(...)]`) to enforce security invariants such as signer validation, owner checks, and mutability. Forgetting or misconfiguring these attributes frequently leads to severe vulnerabilities (e.g., arbitrary account takeover or unauthorized state mutation). `AnchorSecLint` provides rapid static analysis against common vulnerability patterns in Rust-based Anchor source files without requiring complex LLVM or heavy compiler toolchains.

## How It Works
`AnchorSecLint` scans source code line-by-line using precise regular expression heuristic patterns designed to identify:
- **`UncheckedAccount` usage (`SEC-001`)**: Highlights raw unchecked accounts that bypass Anchor automatic validation.
- **`AccountInfo` usage (`SEC-002`)**: Flags low-level `AccountInfo` declarations requiring manual checks.
- **Mutable accounts without signers (`SEC-003`)**: Flags potential missing authority constraints.
- **Manual key comparisons (`SEC-004`)**: Warns against error-prone manual key inequality checks instead of native Anchor constraints.

## Running Tests
Run unit tests completely offline using `pytest`:

