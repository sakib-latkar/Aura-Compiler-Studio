# compiler_types.py
class Token:
    def __init__(self, token_type: str, value: str, line: int):
        self.type = token_type  # e.g., 'KEYWORD', 'ID', 'INT_LIT', 'FLOAT_LIT', 'STRING_LIT', 'BOOL_LIT', 'ASSIGN', 'RELOP', 'SEMI'
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', Line:{self.line})"


class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class VarDeclNode(ASTNode):
    def __init__(self, var_type: str, name: str, expr: ASTNode):
        self.var_type = var_type
        self.name = name
        self.expr = expr

class AssignNode(ASTNode):
    def __init__(self, name: str, expr: ASTNode):
        self.name = name
        self.expr = expr

class BinOpNode(ASTNode):
    def __init__(self, left: ASTNode, op: str, right: ASTNode):
        self.left = left
        self.op = op
        self.right = right

class NumNode(ASTNode):
    def __init__(self, value, val_type: str = 'int'):
        self.value = value
        self.val_type = val_type  # 'int' or 'float'

class StringNode(ASTNode):
    def __init__(self, value: str):
        self.value = value

class BoolNode(ASTNode):
    def __init__(self, value: bool):
        self.value = value

class VarRefNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

class PrintNode(ASTNode):
    def __init__(self, expr: ASTNode):
        self.expr = expr

class IfNode(ASTNode):
    def __init__(self, condition: ASTNode, then_branch: list, else_branch: list = None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch or []

class WhileNode(ASTNode):
    def __init__(self, condition: ASTNode, body: list):
        self.condition = condition
        self.body = body


class TACInstruction:
    def __init__(self, op: str, arg1: str = None, arg2: str = None, result: str = None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __repr__(self):
        if self.op in ('JUMP_IF_FALSE', 'IF_FALSE'):
            return f"IF_FALSE {self.arg1} GOTO {self.result}"
        if self.op == 'GOTO':
            return f"GOTO {self.result}"
        if self.op == 'LABEL':
            return f"LABEL {self.result}:"
        if self.op == '=':
            return f"{self.result} = {self.arg1}"
        if self.op == 'PRINT':
            return f"PRINT {self.arg1}"
        if self.arg2:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        return f"{self.op} {self.arg1} {self.arg2} -> {self.result}"