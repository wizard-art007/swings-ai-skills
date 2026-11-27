import re
import collections

Token = collections.namedtuple('Token', ['type', 'value'])

def lex(code):
    token_specs = [
        ('NUMBER',   r'\d+'),
        ('STRING',   r'"[^"]*"'),
        ('ASSIGN',   r'->'),
        ('IF',       r'unless'),
        ('SPEAK',    r'speak'),
        ('LBRACE',   r'\{'),
        ('RBRACE',   r'\}'),
        ('OP',       r'[+\-*/><=]+'),
        ('IDENT',    r'[a-zA-Z_]\w*'),
        ('NEWLINE',  r'\n'),
        ('SKIP',     r'[ \t]+'),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specs)
    tokens = []
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP' or kind == 'NEWLINE': continue
        elif kind == 'STRING': value = value[1:-1]
        tokens.append(Token(kind, value))
    return tokens

class Interpreter:
    def __init__(self):
        self.vars = {}
        self.output = []

    def run(self, code):
        self.tokens = lex(code)
        self.pos = 0
        while self.pos < len(self.tokens):
            self.statement()
        return self.output

    def peek(self): return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type=None):
        tok = self.peek()
        if expected_type and tok.type != expected_type: raise SyntaxError(f"Expected {expected_type}")
        self.pos += 1
        return tok

    def expression(self):
        left = self.consume().value
        if self.peek() and self.peek().type == 'OP':
            op = self.consume().value
            right = self.consume().value
            l = int(left) if left.isdigit() else self.vars.get(left, left)
            r = int(right) if right.isdigit() else self.vars.get(right, right)
            if op == '+': return l + r
            if op == '-': return l - r
            if op == '*': return l * r
            if op == '/': return l / r
            if op == '==': return l == r
            if op == '>': return l > r
            if op == '<': return l < r
        return int(left) if isinstance(left, str) and left.isdigit() else self.vars.get(left, left)

    def statement(self):
        tok = self.peek()
        if tok.type == 'SPEAK':
            self.consume()
            val = self.expression()
            self.output.append(val)
        elif tok.type == 'IF':
            self.consume()
            cond = self.expression()
            if self.peek().type == 'LBRACE':
                self.consume()
                body = []
                while self.peek().type != 'RBRACE':
                    body.append(self.tokens[self.pos])
                    self.pos += 1
                self.consume('RBRACE')
                if not cond:
                    temp_interp = Interpreter()
                    temp_interp.vars = self.vars.copy()
                    temp_interp.tokens = body
                    temp_interp.pos = 0
                    while temp_interp.pos < len(body): temp_interp.statement()
                    self.output.extend(temp_interp.output)
        else:
            val = self.expression()
            if self.peek() and self.peek().type == 'ASSIGN':
                self.consume('ASSIGN')
                name = self.consume('IDENT').value
                self.vars[name] = val
