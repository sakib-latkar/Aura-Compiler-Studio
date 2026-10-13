# parser.py
from compiler_types import (
    ProgramNode, VarDeclNode, AssignNode, BinOpNode, 
    NumNode, StringNode, BoolNode, VarRefNode, PrintNode, 
    IfNode, WhileNode
)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None

    def error(self, message):
        if self.current_token:
            raise SyntaxError(f"Syntax Error: {message} at '{self.current_token.value}' (Line {self.current_token.line})")
        raise SyntaxError(f"Syntax Error: {message} at End of File")

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, token_type, expected_value=None):
        if self.current_token and self.current_token.type == token_type:
            if expected_value and self.current_token.value != expected_value:
                self.error(f"Expected '{expected_value}', got '{self.current_token.value}'")
            token = self.current_token
            self.advance()
            return token
        got = self.current_token.type if self.current_token else "EOF"
        self.error(f"Expected '{token_type}', got '{got}'")

    def parse(self):
        statements = []
        while self.current_token is not None:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return ProgramNode(statements)

    def parse_statement(self):
        if self.current_token.type == 'KEYWORD':
            val = self.current_token.value
            if val in ('int', 'float', 'string', 'bool'):
                return self.parse_var_decl()
            elif val == 'print':
                return self.parse_print()
            elif val == 'if':
                return self.parse_if()
            elif val == 'while':
                return self.parse_while()
        elif self.current_token.type == 'ID':
            return self.parse_assignment()

        self.error(f"Unexpected statement start '{self.current_token.value}'")

    def parse_block(self):
        self.consume('LBRACE')
        stmts = []
        while self.current_token and self.current_token.type != 'RBRACE':
            stmts.append(self.parse_statement())
        self.consume('RBRACE')
        return stmts

    def parse_var_decl(self):
        vtype = self.consume('KEYWORD').value
        var_name = self.consume('ID').value
        self.consume('ASSIGN')
        expr = self.parse_expression()
        self.consume('SEMI')
        return VarDeclNode(vtype, var_name, expr)

    def parse_assignment(self):
        var_name = self.consume('ID').value
        self.consume('ASSIGN')
        expr = self.parse_expression()
        self.consume('SEMI')
        return AssignNode(var_name, expr)

    def parse_print(self):
        self.consume('KEYWORD', 'print')
        self.consume('LPAREN')
        expr = self.parse_expression()
        self.consume('RPAREN')
        self.consume('SEMI')
        return PrintNode(expr)

    def parse_if(self):
        self.consume('KEYWORD', 'if')
        self.consume('LPAREN')
        cond = self.parse_expression()
        self.consume('RPAREN')
        then_block = self.parse_block()
        else_block = []
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'else':
            self.advance()
            else_block = self.parse_block()
        return IfNode(cond, then_block, else_block)

    def parse_while(self):
        self.consume('KEYWORD', 'while')
        self.consume('LPAREN')
        cond = self.parse_expression()
        self.consume('RPAREN')
        body = self.parse_block()
        return WhileNode(cond, body)

    def parse_expression(self):
        node = self.parse_arithmetic()
        if self.current_token and self.current_token.type == 'RELOP':
            op = self.current_token.value
            self.advance()
            right = self.parse_arithmetic()
            return BinOpNode(left=node, op=op, right=right)
        return node

    def parse_arithmetic(self):
        node = self.parse_term()
        while self.current_token and self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token.value
            self.advance()
            node = BinOpNode(left=node, op=op, right=self.parse_term())
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token and self.current_token.type in ('MUL', 'DIV'):
            op = self.current_token.value
            self.advance()
            node = BinOpNode(left=node, op=op, right=self.parse_factor())
        return node

    def parse_factor(self):
        token = self.current_token
        if not token:
            self.error("Unexpected end of expression")

        if token.type == 'INT_LIT':
            self.advance()
            return NumNode(int(token.value), 'int')
        elif token.type == 'FLOAT_LIT':
            self.advance()
            return NumNode(float(token.value), 'float')
        elif token.type == 'STRING_LIT':
            self.advance()
            return StringNode(token.value)
        elif token.type == 'BOOL_LIT':
            self.advance()
            return BoolNode(token.value == 'true')
        elif token.type == 'ID':
            self.advance()
            return VarRefNode(token.value)
        elif token.type == 'LPAREN':
            self.advance()
            node = self.parse_expression()
            self.consume('RPAREN')
            return node

        self.error(f"Invalid factor '{token.value}'")


def render_ast_ascii(node, indent="", is_last=True):
    lines = []
    marker = "└── " if is_last else "├── "

    if isinstance(node, ProgramNode):
        lines.append("Program [Root]")
        for i, stmt in enumerate(node.statements):
            lines.extend(render_ast_ascii(stmt, indent, i == len(node.statements) - 1))
    elif isinstance(node, VarDeclNode):
        lines.append(f"{indent}{marker}VarDecl ({node.var_type} '{node.name}')")
        lines.extend(render_ast_ascii(node.expr, indent + ("    " if is_last else "│   "), True))
    elif isinstance(node, AssignNode):
        lines.append(f"{indent}{marker}Assign ('{node.name}')")
        lines.extend(render_ast_ascii(node.expr, indent + ("    " if is_last else "│   "), True))
    elif isinstance(node, BinOpNode):
        lines.append(f"{indent}{marker}BinaryOp ('{node.op}')")
        c_indent = indent + ("    " if is_last else "│   ")
        lines.extend(render_ast_ascii(node.left, c_indent, False))
        lines.extend(render_ast_ascii(node.right, c_indent, True))
    elif isinstance(node, NumNode):
        lines.append(f"{indent}{marker}Literal {node.val_type.upper()} ({node.value})")
    elif isinstance(node, StringNode):
        lines.append(f'{indent}{marker}Literal STRING ("{node.value}")')
    elif isinstance(node, BoolNode):
        lines.append(f"{indent}{marker}Literal BOOL ({node.value})")
    elif isinstance(node, VarRefNode):
        lines.append(f"{indent}{marker}VarRef ('{node.name}')")
    elif isinstance(node, PrintNode):
        lines.append(f"{indent}{marker}Print")
        lines.extend(render_ast_ascii(node.expr, indent + ("    " if is_last else "│   "), True))
    elif isinstance(node, IfNode):
        lines.append(f"{indent}{marker}IfCondition")
        c_indent = indent + ("    " if is_last else "│   ")
        lines.extend(render_ast_ascii(node.condition, c_indent, False))
        lines.append(f"{c_indent}├── ThenBlock")
        for s in node.then_branch:
            lines.extend(render_ast_ascii(s, c_indent + "│   ", False))
        if node.else_branch:
            lines.append(f"{c_indent}└── ElseBlock")
            for s in node.else_branch:
                lines.extend(render_ast_ascii(s, c_indent + "    ", True))
    elif isinstance(node, WhileNode):
        lines.append(f"{indent}{marker}WhileLoop")
        c_indent = indent + ("    " if is_last else "│   ")
        lines.extend(render_ast_ascii(node.condition, c_indent, False))
        lines.append(f"{c_indent}└── BodyBlock")
        for s in node.body:
            lines.extend(render_ast_ascii(s, c_indent + "    ", True))

    return lines