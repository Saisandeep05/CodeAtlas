import ast
import os
from typing import List, Dict, Any

class RawAstExtractor(ast.NodeVisitor):
    def __init__(self, file_path: str, module_name: str, source_code: str):
        self.file_path = file_path
        self.module_name = module_name
        self.source_code = source_code.splitlines()
        
        self.classes: List[Dict[str, Any]] = []
        self.functions: List[Dict[str, Any]] = []
        self.imports: List[Dict[str, Any]] = []
        self.calls: List[Dict[str, Any]] = []
        
        self.current_class = None
        self.current_function = None

    def _get_line_text(self, lineno: int) -> str:
        if lineno and 1 <= lineno <= len(self.source_code):
            return self.source_code[lineno - 1].strip()
        return ""

    def _extract_decorator_name(self, dec_node: ast.expr) -> str:
        if isinstance(dec_node, ast.Name):
            return dec_node.id
        elif isinstance(dec_node, ast.Attribute):
            return f"{self._extract_decorator_name(dec_node.value)}.{dec_node.attr}"
        elif isinstance(dec_node, ast.Call):
            return self._extract_decorator_name(dec_node.func)
        return ""

    def visit_ClassDef(self, node: ast.ClassDef):
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr)

        decorators = [self._extract_decorator_name(d) for d in node.decorator_list if self._extract_decorator_name(d)]

        class_info = {
            "type": "class",
            "name": node.name,
            "file": self.file_path,
            "module": self.module_name,
            "line": node.lineno,
            "bases": bases,
            "decorators": decorators,
            "evidence": self._get_line_text(node.lineno)
        }
        self.classes.append(class_info)
        
        prev_class = self.current_class
        self.current_class = class_info
        
        self.generic_visit(node)
        self.current_class = prev_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._handle_function_def(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._handle_function_def(node, is_async=True)
        
    def _handle_function_def(self, node, is_async: bool = False):
        decorators = [self._extract_decorator_name(d) for d in node.decorator_list if self._extract_decorator_name(d)]
        is_property = "property" in decorators
        is_staticmethod = "staticmethod" in decorators

        func_info = {
            "type": "function",
            "name": node.name,
            "file": self.file_path,
            "module": self.module_name,
            "line": node.lineno,
            "parent_class": self.current_class["name"] if self.current_class else None,
            "is_async": is_async,
            "is_property": is_property,
            "is_staticmethod": is_staticmethod,
            "decorators": decorators,
            "evidence": self._get_line_text(node.lineno)
        }
        self.functions.append(func_info)
        
        prev_func = self.current_function
        self.current_function = func_info
        
        self.generic_visit(node)
        self.current_function = prev_func

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append({
                "type": "import",
                "module": alias.name,
                "asname": alias.asname,
                "name": None,
                "file": self.file_path,
                "line": node.lineno,
                "evidence": self._get_line_text(node.lineno)
            })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module if node.module else ""
        level = node.level if node.level else 0
        for alias in node.names:
            self.imports.append({
                "type": "import_from",
                "module": module,
                "name": alias.name,
                "asname": alias.asname,
                "level": level,
                "file": self.file_path,
                "line": node.lineno,
                "evidence": self._get_line_text(node.lineno)
            })
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Ignore standalone super() call when it is the child of super().method()
        if isinstance(node.func, ast.Name) and node.func.id == "super":
            # Don't add standalone 'super()' call to calls list
            self.generic_visit(node)
            return

        callee_expr = ""
        is_attribute = False
        
        if isinstance(node.func, ast.Name):
            callee_expr = node.func.id
        elif isinstance(node.func, ast.Attribute):
            is_attribute = True
            if isinstance(node.func.value, ast.Name):
                callee_expr = f"{node.func.value.id}.{node.func.attr}"
            elif isinstance(node.func.value, ast.Call) and isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == "super":
                callee_expr = f"super().{node.func.attr}"
            else:
                callee_expr = node.func.attr
                
        if callee_expr:
            self.calls.append({
                "type": "call",
                "caller_func": self.current_function["name"] if self.current_function else None,
                "caller_class": self.current_class["name"] if self.current_class else None,
                "callee": callee_expr,
                "is_attribute": is_attribute,
                "file": self.file_path,
                "line": node.lineno,
                "evidence": self._get_line_text(node.lineno)
            })
            
        self.generic_visit(node)

def parse_file(file_path: str, repo_root: str) -> Dict[str, Any]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        return {"error": str(e), "file": file_path}

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"Syntax error: {e}", "file": file_path}

    rel_path = os.path.relpath(file_path, repo_root).replace("\\", "/")
    module_name = os.path.splitext(rel_path)[0].replace("/", ".")

    extractor = RawAstExtractor(rel_path, module_name, source)
    extractor.visit(tree)

    return {
        "file": rel_path,
        "module": module_name,
        "classes": extractor.classes,
        "functions": extractor.functions,
        "imports": extractor.imports,
        "calls": extractor.calls
    }
