# gui_app.py
# MODERN COMPILER STUDIO IDE (FULL 6-PHASE PIPELINE WITH EXTENDED LANGUAGE FEATURES)

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os

from lexer import Lexer
from parser import Parser, render_ast_ascii
from semantic import SemanticAnalyzer
from icg import IntermediateCodeGenerator
from optimizer import CodeOptimizer
from codegen import CodeGenerator


class TextWithLineNumbers(tk.Frame):
    """Custom Code Editor Widget with Line Numbering Margin"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, bg="#0d1117")
        self.text = scrolledtext.ScrolledText(
            self, font=("Consolas", 11), bg="#161b22", fg="#c9d1d9",
            insertbackground="#58a6ff", selectbackground="#1f6feb", bd=0
        )
        self.line_numbers = tk.Text(
            self, width=4, font=("Consolas", 11), bg="#0d1117", fg="#484f58",
            bd=0, state="disabled"
        )
        self.line_numbers.pack(side="left", fill="y", padx=(2, 0))
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<KeyRelease>", self.update_lines)
        self.text.bind("<MouseWheel>", self.update_lines)
        self.update_lines()

    def update_lines(self, event=None):
        content = self.text.get("1.0", "end-1c")
        lines = content.count("\n") + 1
        line_str = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_str)
        self.line_numbers.config(state="disabled")

    def get_code(self):
        return self.text.get("1.0", tk.END)

    def set_code(self, code_str):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", code_str)
        self.update_lines()


class CompilerStudioIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Aura Compiler Studio — Language Engineering IDE")
        self.root.geometry("1020x750")
        self.root.config(bg="#090d16")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TPanedwindow", background="#090d16")
        style.configure("Sash", sashthickness=6, gripcount=0, background="#1f2937")
        style.configure("TNotebook", background="#090d16", borderwidth=0)
        style.configure("TNotebook.Tab", background="#161b22", foreground="#8b949e", padding=[12, 6], font=("Arial", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#1f6feb")], foreground=[("selected", "#ffffff")])

        # 1. Header Bar
        header = tk.Frame(root, bg="#161b22", height=45)
        header.pack(fill="x")
        tk.Label(header, text="⚡ AURA COMPILER STUDIO", font=("Consolas", 13, "bold"), bg="#161b22", fg="#58a6ff").pack(side="left", padx=15, pady=8)

        # 2. Pipeline Stage Status Indicators
        self.badge_frame = tk.Frame(root, bg="#0d1117", pady=4)
        self.badge_frame.pack(fill="x")
        self.badges = {}
        stages = [("L1: Lexer", "#0284c7"), ("L2: Parser", "#2563eb"), ("L3: Semantic", "#7c3aed"),
                  ("L4: ICG", "#d97706"), ("L5: Optimizer", "#9333ea"), ("L6: CodeGen", "#16a34a")]
        for name, color in stages:
            lbl = tk.Label(self.badge_frame, text=f" ● {name} ", font=("Consolas", 8, "bold"), bg="#161b22", fg="#484f58", padx=8, pady=2)
            lbl.pack(side="left", padx=5)
            self.badges[name] = (lbl, color)

        # 3. Resizable Vertical Split Panels (VS Code Style)
        self.paned_window = ttk.PanedWindow(root, orient=tk.VERTICAL)
        self.paned_window.pack(fill="both", expand=True, padx=12, pady=8)

        # Top Pane: Source Code Editor
        editor_pane = tk.Frame(self.paned_window, bg="#090d16")
        self.paned_window.add(editor_pane, weight=1)
        tk.Label(editor_pane, text="SOURCE EDITOR (.src)", font=("Consolas", 9, "bold"), bg="#090d16", fg="#8b949e").pack(anchor="w", pady=(0, 2))
        self.editor = TextWithLineNumbers(editor_pane)
        self.editor.pack(fill="both", expand=True, pady=(0, 4))
        
        # Sample Code Demonstrating Extended Syntax Features
        self.editor.set_code(
            'int count = 1;\n'
            'while (count <= 3) {\n'
            '    print("Loop iteration:");\n'
            '    print(count);\n'
            '    count = count + 1;\n'
            '}\n\n'
            'if (count > 3) {\n'
            '    print("Loop finished successfully!");\n'
            '}'
        )

        # Bottom Pane: Toolbar & Output Console
        output_pane = tk.Frame(self.paned_window, bg="#090d16")
        self.paned_window.add(output_pane, weight=1)

        btn_bar = tk.Frame(output_pane, bg="#090d16")
        btn_bar.pack(fill="x", pady=(4, 6))

        tk.Button(btn_bar, text="▶ Run Lexer (P1)", bg="#0284c7", fg="white", font=("Arial", 9, "bold"), bd=0, padx=10, pady=4, command=self.run_phase1).pack(side="left", padx=3)
        tk.Button(btn_bar, text="🌳 Run Parser (P2)", bg="#2563eb", fg="white", font=("Arial", 9, "bold"), bd=0, padx=10, pady=4, command=self.run_phase2).pack(side="left", padx=3)
        tk.Button(btn_bar, text="🛡️ Semantic (P3)", bg="#7c3aed", fg="white", font=("Arial", 9, "bold"), bd=0, padx=10, pady=4, command=self.run_phase3).pack(side="left", padx=3)
        tk.Button(btn_bar, text="⚙️ ICG (P4)", bg="#d97706", fg="white", font=("Arial", 9, "bold"), bd=0, padx=10, pady=4, command=self.run_phase4).pack(side="left", padx=3)
        tk.Button(btn_bar, text="⚡ Optimize (P5)", bg="#9333ea", fg="white", font=("Arial", 9, "bold"), bd=0, padx=10, pady=4, command=self.run_phase5).pack(side="left", padx=3)
        tk.Button(btn_bar, text="🚀 Build .EXE (P6)", bg="#16a34a", fg="white", font=("Arial", 9, "bold"), bd=0, padx=10, pady=4, command=self.run_phase6).pack(side="left", padx=3)

        self.notebook = ttk.Notebook(output_pane)
        self.notebook.pack(fill="both", expand=True)

        self.tab_frames = []
        self.tab_tokens = self.add_tab("1. Lexer Tokens")
        self.tab_ast = self.add_tab("2. AST Tree")
        self.tab_symbol = self.add_tab("3. Symbol Table")
        self.tab_tac = self.add_tab("4. 3-Address Code")
        self.tab_opt = self.add_tab("5. Optimized IR")
        self.tab_codegen = self.add_tab("6. EXE Output")

    def add_tab(self, title):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        self.tab_frames.append(frame)
        txt = scrolledtext.ScrolledText(frame, font=("Consolas", 10), bg="#0d1117", fg="#3fb950", bd=0, insertbackground="white")
        txt.pack(fill="both", expand=True)
        return txt

    def highlight_badge(self, name):
        for badge_name, (lbl, active_color) in self.badges.items():
            if badge_name == name:
                lbl.config(bg=active_color, fg="#ffffff")
            else:
                lbl.config(bg="#161b22", fg="#484f58")

    def switch_tab(self, index):
        try:
            self.notebook.select(self.tab_frames[index])
        except Exception:
            pass

    # --- PIPELINE HANDLERS ---
    def run_phase1(self):
        """Phase 1: Lexical Analysis"""
        source = self.editor.get_code()
        try:
            tokens = Lexer(source).tokenize()
        except Exception as e:
            messagebox.showerror("Lexical Error", str(e))
            return

        self.tab_tokens.delete("1.0", tk.END)
        self.tab_tokens.insert(tk.END, "=== PHASE 1: TOKEN STREAM OUTPUT ===\n\n")
        for t in tokens:
            self.tab_tokens.insert(tk.END, f"{t}\n")

        self.highlight_badge("L1: Lexer")
        self.switch_tab(0)

    def run_phase2(self):
        """Phase 2: Syntax Analysis (Parser)"""
        source = self.editor.get_code()
        try:
            tokens = Lexer(source).tokenize()
            ast_root = Parser(tokens).parse()
        except Exception as e:
            messagebox.showerror("Syntax Error", str(e))
            return

        self.tab_ast.delete("1.0", tk.END)
        self.tab_ast.insert(tk.END, "=== PHASE 2: ABSTRACT SYNTAX TREE (AST) ===\n\n")
        ascii_lines = render_ast_ascii(ast_root)
        for line in ascii_lines:
            self.tab_ast.insert(tk.END, f"{line}\n")

        self.highlight_badge("L2: Parser")
        self.switch_tab(1)

    def run_phase3(self):
        """Phase 3: Semantic Analysis & Symbol Table"""
        source = self.editor.get_code()
        try:
            tokens = Lexer(source).tokenize()
            ast_root = Parser(tokens).parse()
            analyzer = SemanticAnalyzer()
            symbol_table = analyzer.analyze(ast_root)
        except Exception as e:
            messagebox.showerror("Semantic Error", str(e))
            return

        self.tab_symbol.delete("1.0", tk.END)
        self.tab_symbol.insert(tk.END, "=== PHASE 3: SYMBOL TABLE & SEMANTIC CHECK ===\n\n")

        self.tab_symbol.insert(tk.END, f"{'IDENTIFIER':<15} | {'TYPE':<10} | {'SCOPE':<8}\n")
        self.tab_symbol.insert(tk.END, "-" * 45 + "\n")
        for sym in symbol_table.symbols.values():
            self.tab_symbol.insert(tk.END, f"{sym.name:<15} | {sym.type:<10} | {sym.scope_level:<8}\n")

        self.tab_symbol.insert(tk.END, "\n[✓] Semantic Validation Passed: 0 Errors Found.\n")

        self.highlight_badge("L3: Semantic")
        self.switch_tab(2)

    def run_phase4(self):
        """Phase 4: Intermediate Code Generation (TAC)"""
        source = self.editor.get_code()
        try:
            tokens = Lexer(source).tokenize()
            ast_root = Parser(tokens).parse()
            SemanticAnalyzer().analyze(ast_root)
            icg = IntermediateCodeGenerator()
            tac_list = icg.generate(ast_root)
        except Exception as e:
            messagebox.showerror("ICG Error", str(e))
            return

        self.tab_tac.delete("1.0", tk.END)
        self.tab_tac.insert(tk.END, "=== PHASE 4: THREE-ADDRESS CODE (TAC) ===\n\n")
        for i, tac in enumerate(tac_list, 1):
            self.tab_tac.insert(tk.END, f"({i}) {tac}\n")

        self.highlight_badge("L4: ICG")
        self.switch_tab(3)

    def run_phase5(self):
        """Phase 5: Intermediate Code Optimization"""
        source = self.editor.get_code()
        try:
            tokens = Lexer(source).tokenize()
            ast_root = Parser(tokens).parse()
            SemanticAnalyzer().analyze(ast_root)
            raw_tac = IntermediateCodeGenerator().generate(ast_root)
            opt_tac = CodeOptimizer().optimize(raw_tac)
        except Exception as e:
            messagebox.showerror("Optimization Error", str(e))
            return

        self.tab_opt.delete("1.0", tk.END)
        self.tab_opt.insert(tk.END, "=== PHASE 5: OPTIMIZED INTERMEDIATE CODE ===\n\n")
        self.tab_opt.insert(tk.END, "--- APPLIED OPTIMIZATIONS ---\n")
        self.tab_opt.insert(tk.END, "[✓] Constant Folding (Evaluated static operations)\n")
        self.tab_opt.insert(tk.END, "[✓] Redundant Copy Elimination (Propagated temporaries)\n\n")

        self.tab_opt.insert(tk.END, "--- OPTIMIZED TAC INSTRUCTIONS ---\n")
        for i, tac in enumerate(opt_tac, 1):
            self.tab_opt.insert(tk.END, f"({i}) {tac}\n")

        reduction = len(raw_tac) - len(opt_tac)
        self.tab_opt.insert(tk.END, f"\n[⚡] Optimization Complete: Reduced {len(raw_tac)} -> {len(opt_tac)} instructions ({reduction} instructions saved).\n")

        self.highlight_badge("L5: Optimizer")
        self.switch_tab(4)

    def run_phase6(self):
        """Phase 6: Code Generation & EXE Build"""
        source = self.editor.get_code()
        self.tab_codegen.delete("1.0", tk.END)
        self.tab_codegen.insert(tk.END, "=== PHASE 6: TARGET CODE GENERATION & COMPILATION ===\n\n")

        try:
            # Execute full pipeline end-to-end
            tokens = Lexer(source).tokenize()
            ast_root = Parser(tokens).parse()
            SemanticAnalyzer().analyze(ast_root)
            raw_tac = IntermediateCodeGenerator().generate(ast_root)
            opt_tac = CodeOptimizer().optimize(raw_tac)

            # Generate Target Code
            target_python_code = CodeGenerator().generate_code(opt_tac)

            with open("output.py", "w") as f:
                f.write(target_python_code)

            self.tab_codegen.insert(tk.END, "[✓] Target Python Code Generated ('output.py'):\n")
            self.tab_codegen.insert(tk.END, "-" * 50 + "\n")
            self.tab_codegen.insert(tk.END, f"{target_python_code}\n")
            self.tab_codegen.insert(tk.END, "-" * 50 + "\n\n")

        except Exception as e:
            messagebox.showerror("Compilation Pipeline Error", f"Cannot build EXE. Front-end error:\n{e}")
            return

        self.tab_codegen.insert(tk.END, "[+] Invoking PyInstaller to produce 'output.exe'...\n")
        self.root.update()

        try:
            subprocess.run(["pyinstaller", "--onefile", "--distpath", "./", "output.py"], check=True)
            self.tab_codegen.insert(tk.END, "\n[✓] SUCCESS: Executable created as 'output.exe' in project root!\n")
            messagebox.showinfo("Success", "Full 6-Phase Compilation Succeeded!\n'output.exe' created.")
        except Exception as e:
            self.tab_codegen.insert(tk.END, f"\n[X] Error generating EXE: {e}\n")

        self.highlight_badge("L6: CodeGen")
        self.switch_tab(5)


if __name__ == "__main__":
    root = tk.Tk()
    app = CompilerStudioIDE(root)
    root.mainloop()