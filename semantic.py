# semantic.py
from compiler_types import (
    ProgramNode, VarDeclNode, AssignNode, BinOpNode, 
    NumNode, StringNode, BoolNode, VarRefNode, PrintNode, 
    IfNode, WhileNode
)

class Symbol:
    def __init__(self, name: str, type_: str, scope_level: int = 0):
        self.name = name
        self.type = type_
        self.scope_level = scope_level


class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def insert(self, symbol: Symbol):
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Symbol:
        return self.symbols.get(name)

    def is_declared(self, name: str) -> bool:
        return name in self.symbols


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

    def error(self, message: str):
        self.errors.append(f"Semantic Error: {message}")

    def analyze(self, ast_root: ProgramNode) -> SymbolTable:
        self.visit(ast_root)
        if self.errors:
            raise ValueError("\n".join(self.errors))
        return self.symbol_table

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No visit_{type(node).__name__} defined.")

    def visit_ProgramNode(self, node: ProgramNode):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDeclNode(self, node: VarDeclNode):
        if self.symbol_table.is_declared(node.name):
            self.error(f"Variable '{node.name}' is already declared.")
            return

        expr_type = self.visit(node.expr)

        if expr_type != 'unknown':
            # Allow implicit int -> float widening
            if node.var_type == 'float' and expr_type in ('int', 'float'):
                pass
            elif expr_type != node.var_type:
                self.error(f"Cannot assign '{expr_type}' to variable '{node.name}' of type '{node.var_type}'.")

        self.symbol_table.insert(Symbol(node.name, node.var_type))

    def visit_AssignNode(self, node: AssignNode):
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self.error(f"Variable '{node.name}' assigned before declaration.")
            return

        expr_type = self.visit(node.expr)
        if expr_type != 'unknown':
            if symbol.type == 'float' and expr_type in ('int', 'float'):
                pass
            elif expr_type != symbol.type:
                self.error(f"Cannot assign '{expr_type}' to '{node.name}' of type '{symbol.type}'.")

    def visit_BinOpNode(self, node: BinOpNode) -> str:
        ltype = self.visit(node.left)
        rtype = self.visit(node.right)

        if ltype == 'unknown' or rtype == 'unknown':
            return 'unknown'

        # Relational Operators (==, !=, <, >, <=, >=) -> Returns 'bool'
        if node.op in ('==', '!=', '<', '>', '<=', '>='):
            if ltype in ('int', 'float') and rtype in ('int', 'float'):
                return 'bool'
            if ltype == rtype:
                return 'bool'
            self.error(f"Cannot compare type '{ltype}' with '{rtype}'.")
            return 'unknown'

        # Arithmetic Operators (+, -, *, /)
        if ltype in ('int', 'float') and rtype in ('int', 'float'):
            return 'float' if (ltype == 'float' or rtype == 'float') else 'int'

        if node.op == '+' and ltype == 'string' and rtype == 'string':
            return 'string'

        self.error(f"Operator '{node.op}' invalid for types '{ltype}' and '{rtype}'.")
        return 'unknown'

    def visit_NumNode(self, node: NumNode) -> str:
        return node.val_type

    def visit_StringNode(self, node: StringNode) -> str:
        return 'string'

    def visit_BoolNode(self, node: BoolNode) -> str:
        return 'bool'

    def visit_VarRefNode(self, node: VarRefNode) -> str:
        sym = self.symbol_table.lookup(node.name)
        if not sym:
            self.error(f"Variable '{node.name}' referenced before declaration.")
            return 'unknown'
        return sym.type

    def visit_PrintNode(self, node: PrintNode):
        self.visit(node.expr)

    def visit_IfNode(self, node: IfNode):
        cond_type = self.visit(node.condition)
        if cond_type != 'bool' and cond_type != 'unknown':
            self.error(f"If condition must evaluate to 'bool', got '{cond_type}'.")
        for s in node.then_branch:
            self.visit(s)
        for s in node.else_branch:
            self.visit(s)

    def visit_WhileNode(self, node: WhileNode):
        cond_type = self.visit(node.condition)
        if cond_type != 'bool' and cond_type != 'unknown':
            self.error(f"While condition must evaluate to 'bool', got '{cond_type}'.")
        for s in node.body:
            self.visit(s)