#!/usr/bin/env python3
"""Parse Python class definitions using AST and convert them into PlantUML class diagram syntax."""

import ast
import argparse
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple


def _format_ast_node(node: Optional[ast.AST]) -> str:
    """Format an AST node into a string representation."""
    if node is None:
        return ""
    if hasattr(ast, "unparse"):
        try:
            return ast.unparse(node)
        except Exception:
            pass
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return repr(node.value)
    if isinstance(node, ast.Attribute):
        return f"{_format_ast_node(node.value)}.{node.attr}"
    return ""


def _get_visibility(name: str) -> str:
    """Determine UML visibility prefix based on naming conventions."""
    if name.startswith("__") and not name.endswith("__"):
        return "-"  # Private
    if name.startswith("_") and not name.startswith("__"):
        return "#"  # Protected
    return "+"  # Public


def _is_decorator_named(decorator_node: ast.AST, name: str) -> bool:
    """Check if an AST decorator matches the given name."""
    if isinstance(decorator_node, ast.Name) and decorator_node.id == name:
        return True
    if isinstance(decorator_node, ast.Attribute) and decorator_node.attr == name:
        return True
    if isinstance(decorator_node, ast.Call):
        return _is_decorator_named(decorator_node.func, name)
    return False


class ClassDiagramGenerator:
    """Generates PlantUML class diagram from Python AST."""

    def __init__(self, include_private: bool = True):
        self.include_private = include_private

    def _should_include(self, name: str) -> bool:
        """Check if member should be included based on visibility filter."""
        if not self.include_private:
            if name.startswith("__") and not name.endswith("__"):
                return False
        return True

    def _extract_attributes(
        self, class_node: ast.ClassDef
    ) -> List[Tuple[str, str, Optional[str]]]:
        """Extract (visibility, name, type_annotation) for class and instance attributes."""
        attrs = {}

        # 1. Class-level attributes
        for stmt in class_node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                name = stmt.target.id
                if self._should_include(name):
                    type_str = _format_ast_node(stmt.annotation)
                    attrs[name] = (_get_visibility(name), name, type_str)
            elif isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        if self._should_include(name) and name not in attrs:
                            attrs[name] = (_get_visibility(name), name, None)

        # 2. Instance attributes from __init__
        for stmt in class_node.body:
            if (
                isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))
                and stmt.name == "__init__"
            ):
                for sub_node in ast.walk(stmt):
                    if (
                        isinstance(sub_node, ast.AnnAssign)
                        and isinstance(sub_node.target, ast.Attribute)
                        and isinstance(sub_node.target.value, ast.Name)
                        and sub_node.target.value.id == "self"
                    ):
                        name = sub_node.target.attr
                        if self._should_include(name):
                            type_str = _format_ast_node(sub_node.annotation)
                            attrs[name] = (_get_visibility(name), name, type_str)
                    elif isinstance(sub_node, ast.Assign):
                        for target in sub_node.targets:
                            if (
                                isinstance(target, ast.Attribute)
                                and isinstance(target.value, ast.Name)
                                and target.value.id == "self"
                            ):
                                name = target.attr
                                if self._should_include(name) and name not in attrs:
                                    attrs[name] = (_get_visibility(name), name, None)

        return list(attrs.values())

    def _extract_methods(self, class_node: ast.ClassDef) -> List[str]:
        """Extract formatted method signatures from a class node."""
        methods = []

        for stmt in class_node.body:
            if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            name = stmt.name
            if not self._should_include(name):
                continue

            # Determine decorators
            is_static = any(
                _is_decorator_named(dec, "staticmethod")
                for dec in stmt.decorator_list
            )
            is_classmethod = any(
                _is_decorator_named(dec, "classmethod")
                for dec in stmt.decorator_list
            )
            is_abstract = any(
                _is_decorator_named(dec, "abstractmethod")
                for dec in stmt.decorator_list
            )

            # Build modifiers
            modifiers = []
            if is_static or is_classmethod:
                modifiers.append("{static}")
            if is_abstract:
                modifiers.append("{abstract}")

            vis = _get_visibility(name)

            # Build argument list
            args_list = []
            args = stmt.args.args
            start_idx = 0
            if (not is_static) and args:
                first_arg = args[0].arg
                if first_arg in ("self", "cls"):
                    start_idx = 1

            for arg in args[start_idx:]:
                arg_repr = arg.arg
                if arg.annotation:
                    arg_repr += f": {_format_ast_node(arg.annotation)}"
                args_list.append(arg_repr)

            if stmt.args.vararg:
                vararg = f"*{stmt.args.vararg.arg}"
                if stmt.args.vararg.annotation:
                    vararg += f": {_format_ast_node(stmt.args.vararg.annotation)}"
                args_list.append(vararg)

            if stmt.args.kwarg:
                kwarg = f"**{stmt.args.kwarg.arg}"
                if stmt.args.kwarg.annotation:
                    kwarg += f": {_format_ast_node(stmt.args.kwarg.annotation)}"
                args_list.append(kwarg)

            args_str = ", ".join(args_list)

            # Return type
            ret_str = ""
            if stmt.returns:
                ret_str = f": {_format_ast_node(stmt.returns)}"

            prefix = " ".join(modifiers) + (" " if modifiers else "")
            method_str = f"{prefix}{vis}{name}({args_str}){ret_str}"
            methods.append(method_str)

        return methods

    def generate(self, source_code: str) -> str:
        """Generate PlantUML diagram from Python source code."""
        tree = ast.parse(source_code)
        lines = ["@startuml"]

        relationships = []
        classes_found = False

        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue

            classes_found = True
            is_abstract = False
            base_names = []

            for base in node.bases:
                base_name = _format_ast_node(base)
                if base_name in ("ABC", "abc.ABC"):
                    is_abstract = True
                elif base_name and base_name != "object":
                    base_names.append(base_name)
                    relationships.append(f"{base_name} <|-- {node.name}")

            # Check if any method is abstract
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if any(
                        _is_decorator_named(dec, "abstractmethod")
                        for dec in item.decorator_list
                    ):
                        is_abstract = True
                        break

            class_kind = "abstract class" if is_abstract else "class"
            lines.append(f"{class_kind} {node.name} {{")

            # Attributes
            attributes = self._extract_attributes(node)
            for vis, name, type_str in attributes:
                if type_str:
                    lines.append(f"  {vis}{name}: {type_str}")
                else:
                    lines.append(f"  {vis}{name}")

            # Methods
            methods = self._extract_methods(node)
            for m in methods:
                lines.append(f"  {m}")

            lines.append("}")

        if relationships:
            lines.append("")
            lines.extend(relationships)

        lines.append("@enduml")
        return "\n".join(lines)


def parse_source(source_code: str, include_private: bool = True) -> str:
    """Parse raw Python source code and return PlantUML string."""
    generator = ClassDiagramGenerator(include_private=include_private)
    return generator.generate(source_code)


def parse_file(file_path: str, include_private: bool = True) -> str:
    """Parse a Python source file and return PlantUML string."""
    code = Path(file_path).read_text(encoding="utf-8")
    return parse_source(code, include_private=include_private)


def main(argv=None) -> int:
    """CLI entry point for Python-to-PlantUML class diagram generator."""
    parser = argparse.ArgumentParser(
        description="Convert Python class definitions into PlantUML class diagrams."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--input", help="Path to Python source file")
    group.add_argument("-c", "--code", help="Inline Python code string")

    parser.add_argument("-o", "--output", help="Output .puml file path")
    parser.add_argument(
        "--no-private",
        action="store_true",
        help="Exclude private attributes and methods (names starting with __)",
    )

    args = parser.parse_args(argv)

    if args.input:
        content = Path(args.input).read_text(encoding="utf-8")
    else:
        content = args.code

    generator = ClassDiagramGenerator(include_private=not args.no_private)
    puml = generator.generate(content)

    if args.output:
        Path(args.output).write_text(puml, encoding="utf-8")
    else:
        sys.stdout.write(puml + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
