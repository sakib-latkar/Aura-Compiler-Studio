# icg.py
# PHASE 4: INTERMEDIATE CODE GENERATION (TAC with Control Flow & Multi-Type Support)

from compiler_types import (
    ProgramNode, VarDeclNode, AssignNode, BinOpNode, 
    NumNode, StringNode, BoolNode, VarRefNode, PrintNode, 
    IfNode, WhileNode, TACInstruction
)

class IntermediateCodeGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 1
        self.label_count = 1

    def new_temp(self) -> str:
        t = f"t{self.temp_count}"
        self.temp_count += 1
        return t

    def new_label(self) -> str:
        lbl = f"L{self.label_count}"
        self.label_count += 1
        return lbl

    def generate(self, ast_root: ProgramNode):
        self.instructions = []
        self.temp_count = 1
        self.label_count = 1
        self.visit(ast_root)
        return self.instructions

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No {type(node).__name__} handler defined.")

    def visit_ProgramNode(self, node: ProgramNode):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDeclNode(self, node: VarDeclNode):
        res = self.visit(node.expr)
        self.instructions.append(TACInstruction(op="=", arg1=res, result=node.name))

    def visit_AssignNode(self, node: AssignNode):
        res = self.visit(node.expr)
        self.instructions.append(TACInstruction(op="=", arg1=res, result=node.name))

    def visit_BinOpNode(self, node: BinOpNode) -> str:
        l = self.visit(node.left)
        r = self.visit(node.right)
        t = self.new_temp()
        self.instructions.append(TACInstruction(op=node.op, arg1=str(l), arg2=str(r), result=t))
        return t

    def visit_NumNode(self, node: NumNode) -> str:
        return str(node.value)

    def visit_StringNode(self, node: StringNode) -> str:
        return f'"{node.value}"'

    def visit_BoolNode(self, node: BoolNode) -> str:
        return "True" if node.value else "False"

    def visit_VarRefNode(self, node: VarRefNode) -> str:
        return node.name

    def visit_PrintNode(self, node: PrintNode):
        res = self.visit(node.expr)
        self.instructions.append(TACInstruction(op="PRINT", arg1=str(res)))

    def visit_IfNode(self, node: IfNode):
        cond_res = self.visit(node.condition)
        else_lbl = self.new_label()
        end_lbl = self.new_label()

        target_lbl = else_lbl if node.else_branch else end_lbl
        self.instructions.append(TACInstruction(op="JUMP_IF_FALSE", arg1=str(cond_res), result=target_lbl))

        for s in node.then_branch:
            self.visit(s)

        if node.else_branch:
            self.instructions.append(TACInstruction(op="GOTO", result=end_lbl))
            self.instructions.append(TACInstruction(op="LABEL", result=else_lbl))
            for s in node.else_branch:
                self.visit(s)

        self.instructions.append(TACInstruction(op="LABEL", result=end_lbl))

    def visit_WhileNode(self, node: WhileNode):
        start_lbl = self.new_label()
        end_lbl = self.new_label()

        self.instructions.append(TACInstruction(op="LABEL", result=start_lbl))
        cond_res = self.visit(node.condition)
        self.instructions.append(TACInstruction(op="JUMP_IF_FALSE", arg1=str(cond_res), result=end_lbl))

        for s in node.body:
            self.visit(s)

        self.instructions.append(TACInstruction(op="GOTO", result=start_lbl))
        self.instructions.append(TACInstruction(op="LABEL", result=end_lbl))