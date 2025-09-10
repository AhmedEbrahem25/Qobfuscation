import ast
import random
import string


class IdentifierManager:
    """
    Manages the obfuscation of identifiers within Python source code using AST.
    This includes renaming variables, functions, and classes.
    """

    def __init__(self, provided_imports=None):
        self.template_provided_imports = provided_imports or {
            "qiskit", "random", "time", "math", "datetime",
            "base64", "hashlib", "unittest", "ast", "string"
        }

    def _random_identifier(self, prefix: str = "var", length: int = 8) -> str:
        """Generates a random, safe Python identifier."""
        letters = string.ascii_letters + string.digits
        suffix = ''.join(random.choice(letters) for _ in range(length))
        return f"{prefix}_{suffix}"

    def rename_identifiers(self, source_code: str) -> str:
        """
        Parses the source code, removes redundant imports provided by templates,
        and renames all user-defined identifiers.
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return source_code

        # Clean up imports first
        remover = self._ImportRemover(self.template_provided_imports)
        clean_tree = remover.visit(tree)
        ast.fix_missing_locations(clean_tree)

        # Find all identifiers to be renamed
        collector = self._NameCollector()
        collector.visit(clean_tree)
        name_map = {name: self._random_identifier() for name in collector.defined_names}

        if not name_map:
            return ast.unparse(clean_tree)

        # Rename the collected identifiers
        renamer = self._Renamer(name_map)
        final_tree = renamer.visit(clean_tree)
        ast.fix_missing_locations(final_tree)

        return ast.unparse(final_tree)

    # --- Nested helper classes for internal use ---
    class _ImportRemover(ast.NodeTransformer):
        def __init__(self, imports_to_remove):
            self.imports_to_remove = imports_to_remove

        def visit_Import(self, node):
            node.names = [alias for alias in node.names if alias.name not in self.imports_to_remove]
            return node if node.names else None

        def visit_ImportFrom(self, node):
            return None if node.module in self.imports_to_remove else node

    class _NameCollector(ast.NodeVisitor):
        def __init__(self):
            self.defined_names = set()
            self.ignored_names = {"self", "__init__"}

        def visit_FunctionDef(self, node):
            if node.name not in self.ignored_names: self.defined_names.add(node.name)
            for arg in node.args.args:
                if arg.arg not in self.ignored_names: self.defined_names.add(arg.arg)
            self.generic_visit(node)

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id not in self.ignored_names:
                    self.defined_names.add(target.id)
            self.generic_visit(node)

        def visit_ClassDef(self, node):
            if node.name not in self.ignored_names: self.defined_names.add(node.name)
            self.generic_visit(node)

    class _Renamer(ast.NodeTransformer):
        def __init__(self, name_map):
            self.name_map = name_map

        def visit_Name(self, node):
            node.id = self.name_map.get(node.id, node.id)
            return node

        def visit_Attribute(self, node):

            self.generic_visit(node)
            if node.attr in self.name_map:
                node.attr = self.name_map[node.attr]
            return node

        # ----------------------------------------------

        def visit_FunctionDef(self, node):
            node.name = self.name_map.get(node.name, node.name)
            for arg in node.args.args:
                arg.arg = self.name_map.get(arg.arg, arg.arg)
            self.generic_visit(node)
            return node

        def visit_ClassDef(self, node):
            node.name = self.name_map.get(node.name, node.name)
            self.generic_visit(node)
            return node

        def visit_arg(self, node):
            node.arg = self.name_map.get(node.arg, node.arg)
            return node