# lexer.py
import re
from compiler_types import Token

class Lexer:
    KEYWORDS = {'int', 'float', 'string', 'bool', 'print', 'if', 'else', 'while', 'true', 'false'}

    def __init__(self, source_code: str):
        self.source = source_code
        self.line = 1

    def tokenize(self):
        tokens = []
        i = 0
        n = len(self.source)

        while i < n:
            ch = self.source[i]

            if ch == '\n':
                self.line += 1
                i += 1
                continue
            elif ch.isspace():
                i += 1
                continue

            # Strings
            if ch == '"':
                start = i + 1
                i += 1
                while i < n and self.source[i] != '"':
                    if self.source[i] == '\n':
                        self.line += 1
                    i += 1
                if i >= n:
                    raise SyntaxError(f"Lexical Error: Unterminated string at line {self.line}")
                str_val = self.source[start:i]
                tokens.append(Token('STRING_LIT', str_val, self.line))
                i += 1
                continue

            # Multi-character relops
            if self.source[i:i+2] in ('==', '!=', '<=', '>='):
                tokens.append(Token('RELOP', self.source[i:i+2], self.line))
                i += 2
                continue

            # Single character relops
            if ch in ('<', '>'):
                tokens.append(Token('RELOP', ch, self.line))
                i += 1
                continue

            # Delimiters and math ops
            if ch == '=':
                tokens.append(Token('ASSIGN', '=', self.line))
                i += 1
                continue
            elif ch == '+':
                tokens.append(Token('PLUS', '+', self.line))
                i += 1
                continue
            elif ch == '-':
                tokens.append(Token('MINUS', '-', self.line))
                i += 1
                continue
            elif ch == '*':
                tokens.append(Token('MUL', '*', self.line))
                i += 1
                continue
            elif ch == '/':
                tokens.append(Token('DIV', '/', self.line))
                i += 1
                continue
            elif ch == ';':
                tokens.append(Token('SEMI', ';', self.line))
                i += 1
                continue
            elif ch == '(':
                tokens.append(Token('LPAREN', '(', self.line))
                i += 1
                continue
            elif ch == ')':
                tokens.append(Token('RPAREN', ')', self.line))
                i += 1
                continue
            elif ch == '{':
                tokens.append(Token('LBRACE', '{', self.line))
                i += 1
                continue
            elif ch == '}':
                tokens.append(Token('RBRACE', '}', self.line))
                i += 1
                continue

            # Numbers (int and float)
            if ch.isdigit():
                num_str = ""
                is_float = False
                while i < n and (self.source[i].isdigit() or self.source[i] == '.'):
                    if self.source[i] == '.':
                        if is_float:
                            break
                        is_float = True
                    num_str += self.source[i]
                    i += 1
                token_type = 'FLOAT_LIT' if is_float else 'INT_LIT'
                tokens.append(Token(token_type, num_str, self.line))
                continue

            # Identifiers and Keywords
            if ch.isalpha() or ch == '_':
                ident = ""
                while i < n and (self.source[i].isalnum() or self.source[i] == '_'):
                    ident += self.source[i]
                    i += 1
                if ident in self.KEYWORDS:
                    if ident in ('true', 'false'):
                        tokens.append(Token('BOOL_LIT', ident, self.line))
                    else:
                        tokens.append(Token('KEYWORD', ident, self.line))
                else:
                    tokens.append(Token('ID', ident, self.line))
                continue

            raise SyntaxError(f"Lexical Error: Illegal character '{ch}' at line {self.line}")

        return tokens