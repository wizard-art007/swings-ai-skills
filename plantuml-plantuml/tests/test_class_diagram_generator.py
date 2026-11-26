import sys
from pathlib import Path

# Required import style
sys.path.insert(0, "scripts")

import pytest
from class_diagram_generator import (
    ClassDiagramGenerator,
    parse_source,
    parse_file,
    main,
)


def test_basic_class_generation():
    code = """
class Car:
    brand: str
    year: int = 2020

    def drive(self, distance: float) -> bool:
        return True
"""
    puml = parse_source(code)
    assert "@startuml" in puml
    assert "@enduml" in puml
    assert "class Car {" in puml
    assert "+brand: str" in puml
    assert "+year: int" in puml
    assert "+drive(distance: float): bool" in puml


def test_inheritance_relationship():
    code = """
class Animal:
    pass

class Dog(Animal):
    def bark(self) -> None:
        pass
"""
    puml = parse_source(code)
    assert "class Animal {" in puml
    assert "class Dog {" in puml
    assert "Animal <|-- Dog" in puml


def test_abstract_class_and_methods():
    code = """
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Square(Shape):
    side: float

    def area(self) -> float:
        return self.side * self.side
"""
    puml = parse_source(code)
    assert "abstract class Shape {" in puml
    assert "{abstract} +area(): float" in puml
    assert "class Square {" in puml
    assert "Shape <|-- Square" in puml
    assert "ABC <|-- Shape" not in puml  # ABC base should not be rendered as parent link


def test_static_and_class_methods():
    code = """
class MathUtils:
    @staticmethod
    def add(a: int, b: int) -> int:
        return a + b

    @classmethod
    def factory(cls, name: str) -> "MathUtils":
        return cls()
"""
    puml = parse_source(code)
    assert "{static} +add(a: int, b: int): int" in puml
    assert "{static} +factory(name: str): 'MathUtils'" in puml


def test_visibility_and_filter():
    code = """
class Account:
    public_id: str
    _internal_state: int
    __secret_key: str

    def public_action(self) -> None:
        pass

    def _protected_action(self) -> None:
        pass

    def __private_action(self) -> None:
        pass
"""
    # With private members included
    puml_all = parse_source(code, include_private=True)
    assert "+public_id: str" in puml_all
    assert "#_internal_state: int" in puml_all
    assert "-__secret_key: str" in puml_all
    assert "+public_action(): None" in puml_all
    assert "#_protected_action(): None" in puml_all
    assert "-__private_action(): None" in puml_all

    # Without private members
    puml_no_priv = parse_source(code, include_private=False)
    assert "+public_id: str" in puml_no_priv
    assert "#_internal_state: int" in puml_no_priv
    assert "-__secret_key" not in puml_no_priv
    assert "-__private_action" not in puml_no_priv


def test_instance_attributes_in_init():
    code = """
class User:
    def __init__(self, username: str, age: int):
        self.username: str = username
        self.age = age
        self._role = "guest"
"""
    puml = parse_source(code)
    assert "+username: str" in puml
    assert "+age" in puml
    assert "#_role" in puml


def test_parse_file_and_cli(tmp_path, capsys):
    sample_file = tmp_path / "sample.py"
    sample_file.write_text(
        """
class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}"
""",
        encoding="utf-8",
    )

    # Test parse_file
    puml = parse_file(str(sample_file))
    assert "class Greeter {" in puml
    assert "+greet(name: str): str" in puml

    # Test CLI to stdout
    ret = main(["-i", str(sample_file)])
    assert ret == 0
    captured = capsys.readouterr()
    assert "class Greeter {" in captured.out

    # Test CLI to file output
    out_file = tmp_path / "diagram.puml"
    ret = main(["-i", str(sample_file), "-o", str(out_file)])
    assert ret == 0
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "class Greeter {" in content


def test_cli_with_inline_code(capsys):
    ret = main(["-c", "class Foo:\n    x: int = 1"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "class Foo {" in captured.out
    assert "+x: int" in captured.out


def test_syntax_error_handling():
    with pytest.raises(SyntaxError):
        parse_source("class Def Incomplete:")
