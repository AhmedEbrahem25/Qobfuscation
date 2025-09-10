# Qobfuscation_lib/code_splitter.py
import ast
import random
from typing import List, Tuple, Union


class IntelligentCodeSplitter:
    """
    Encapsulates the logic for intelligently splitting Python source code
    by analyzing data dependencies using AST.
    """

    def __init__(self, protected_funcs: List[str] = None):
        self.protected_funcs = protected_funcs if protected_funcs is not None else []

    def split(self, src: str) -> Tuple[str, str]:
        """
        The main public method to split the source code into two logical parts.
        """
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return src, "pass"

        import_nodes, protected_defs, safe_defs, main_block = self._categorize_nodes(tree)

        atomic_groups = self._group_dependent_statements(safe_defs)
        random.shuffle(atomic_groups)

        split_point = len(atomic_groups) // 2
        part1_groups = atomic_groups[:split_point]
        part2_groups = atomic_groups[split_point:]

        part1_defs = [node for group in part1_groups for node in group]
        part2_defs = [node for group in part2_groups for node in group]

        part1_nodes = import_nodes + protected_defs + part1_defs
        part2_nodes = import_nodes + protected_defs + part2_defs
        if main_block:
            part2_nodes.append(main_block)

        return self._safe_unparse(part1_nodes), self._safe_unparse(part2_nodes)

    def _categorize_nodes(self, tree: ast.Module) -> Tuple[list, list, list, ast.If]:
        import_nodes, protected_defs, safe_defs = [], [], []
        main_block = None
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_nodes.append(node)
            elif isinstance(node, ast.FunctionDef) and node.name in self.protected_funcs:
                protected_defs.append(node)
            elif isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
                if getattr(node.test.left, 'id', None) == '__name__':
                    main_block = node
                else:
                    safe_defs.append(node)
            else:
                safe_defs.append(node)
        return import_nodes, protected_defs, safe_defs, main_block

    def _group_dependent_statements(self, statements: List[ast.AST]) -> List[List[ast.AST]]:
        if not statements: return []

        analyzer = _VariableUsageAnalyzer()
        analyzed_nodes = [{'node': node, 'defines': analyzer.analyze(node)[0], 'uses': analyzer.analyze(node)[1]} for
                          node in statements]

        groups = [[node_info] for node_info in analyzed_nodes]

        merged_in_pass = True
        while merged_in_pass:
            merged_in_pass = False
            i = 0
            while i < len(groups):
                j = i + 1
                while j < len(groups):
                    g1_defines = {d for item in groups[i] for d in item['defines']}
                    g2_uses = {u for item in groups[j] for u in item['uses']}
                    g2_defines = {d for item in groups[j] for d in item['defines']}
                    g1_uses = {u for item in groups[i] for u in item['uses']}

                    if g1_defines.intersection(g2_uses) or g2_defines.intersection(g1_uses):
                        groups[i].extend(groups.pop(j))
                        merged_in_pass = True
                    else:
                        j += 1
                i += 1

        return [[item['node'] for item in group] for group in groups]

    def _safe_unparse(self, nodes: List[ast.AST]) -> str:
        try:
            module = ast.Module(body=nodes, type_ignores=[])
            ast.fix_missing_locations(module)
            return ast.unparse(module)
        except Exception:
            return "\n".join([ast.unparse(n) for n in nodes]) if nodes else "pass"


class _VariableUsageAnalyzer(ast.NodeVisitor):
    """
    Analyzes an AST node to find all variables it defines and uses.
    Version 2: Now correctly identifies function and class definitions.
    """
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.used.add(node.id)

    def visit_arg(self, node):
        self.defined.add(node.arg)

    def visit_FunctionDef(self, node):
        self.defined.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.defined.add(node.name)
        self.generic_visit(node)

    def analyze(self, node):
        self.defined, self.used = set(), set()
        self.visit(node)

        if hasattr(node, 'name') and node.name in self.used:
            self.used.remove(node.name)

        return self.defined, self.used