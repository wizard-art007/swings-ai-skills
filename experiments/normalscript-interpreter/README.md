# NormalScript Interpreter

NormalScript is an esoteric toy scripting language focused on "Reverse Assignment" (value -> variable) and expressive keywords like `speak` and `unless`.

## Syntax
- Reverse Assignment: `10 + 5 -> x`
- Output: `speak x`
- Conditionals: `unless condition { ... }`
- Math: Supports `+`, `-`, `*`, `/` and comparisons `==`, `>`, `<`.

## Implementation
The interpreter uses a standard Regex-based lexer and a recursive-descent parser to convert script text into an AST, which is then evaluated against an internal state dictionary.

## How to run
1. Install `pytest`.
2. Run `pytest tests/test_normalscript.py`.

## Lessons Learned
Building a DSL highlights how strict grammars constrain flexibility. Using Python's `re` module for tokenizing is efficient for small languages but requires careful string formatting (specifically avoiding f-string collision with regex groups).
