# optimizer.py
# PHASE 5: CODE OPTIMIZATION (Constant Folding & Redundant Copy Elimination)

from compiler_types import TACInstruction

class CodeOptimizer:
    def __init__(self):
        pass

    def optimize(self, tac_list):
        """Applies optimization passes over the TAC instructions."""
        optimized_tac = self.constant_folding_pass(tac_list)
        optimized_tac = self.copy_propagation_pass(optimized_tac)
        return optimized_tac

    def constant_folding_pass(self, tac_list):
        """Evaluates compile-time constant arithmetic operations."""
        new_tac = []
        for tac in tac_list:
            if tac.op in ('+', '-', '*', '/'):
                # Check if both arguments are numeric constants
                if tac.arg1 and tac.arg2 and tac.arg1.isdigit() and tac.arg2.isdigit():
                    v1 = int(tac.arg1)
                    v2 = int(tac.arg2)
                    res_val = 0
                    if tac.op == '+':
                        res_val = v1 + v2
                    elif tac.op == '-':
                        res_val = v1 - v2
                    elif tac.op == '*':
                        res_val = v1 * v2
                    elif tac.op == '/' and v2 != 0:
                        res_val = v1 // v2

                    # Convert binary op into direct assignment
                    new_tac.append(TACInstruction(op="=", arg1=str(res_val), arg2=None, result=tac.result))
                    continue
            new_tac.append(tac)
        return new_tac

    def copy_propagation_pass(self, tac_list):
        """Simplifies redundant copy assignments like t1 = 15; x = t1 -> x = 15."""
        substitutions = {}
        final_tac = []

        for tac in tac_list:
            # Substitute args if present in active mappings
            arg1 = substitutions.get(tac.arg1, tac.arg1) if tac.arg1 else None
            arg2 = substitutions.get(tac.arg2, tac.arg2) if tac.arg2 else None

            if tac.op == '=':
                # If copying temp to actual variable, bind value directly
                if tac.arg1.startswith('t') and tac.arg1 in substitutions:
                    arg1 = substitutions[tac.arg1]
                
                # Record mapping if assigning a constant/var to temporary
                if tac.result and tac.result.startswith('t'):
                    substitutions[tac.result] = arg1
                    continue
                
                final_tac.append(TACInstruction(op="=", arg1=arg1, arg2=None, result=tac.result))
            else:
                final_tac.append(TACInstruction(op=tac.op, arg1=arg1, arg2=arg2, result=tac.result))

        return final_tac