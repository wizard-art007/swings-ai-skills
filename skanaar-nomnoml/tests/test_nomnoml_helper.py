"""Tests for nomnoml_helper."""

import sys
import unittest.mock as mock
import zlib
import base64
import pytest
import requests

sys.path.insert(0, "scripts")
from nomnoml_helper import (
    parse_text_description,
    get_kroki_url,
    render_nomnoml,
    _ensure_bracketed,
    _format_node,
)


def test_ensure_bracketed():
    assert _ensure_bracketed("User") == "[User]"
    assert _ensure_bracketed("[User]") == "[User]"
    assert _ensure_bracketed("  [User]  ") == "[User]"


def test_format_node():
    assert _format_node("User") == "[User]"
    assert _format_node("User", stereotype="actor") == "[<actor> User]"
    assert _format_node("User", parts=["id: int", "login()"]) == "[User|id: int|login()]"
    assert _format_node("User", stereotype="table", parts=["id INT", "name TEXT"]) == "[<table> User|id INT|name TEXT]"


def test_parse_text_description_stereotypes_and_inheritance():
    text = """
    Admin: actor
    Admin inherits User
    User <:- Customer
    """
    nomnoml = parse_text_description(text)
    assert "[<actor> Admin]" in nomnoml
    assert "[Admin] -:> [User]" in nomnoml
    assert "[User] <:- [Customer]" in nomnoml


def test_parse_text_description_various_arrows():
    text = """
    A -> B
    B <-- C
    C <--> D
    D +-> E
    E o-> F
    F --:> G
    G <:-- H
    H -- I
    """
    nomnoml = parse_text_description(text)
    assert "[A] -> [B]" in nomnoml
    assert "[B] <-- [C]" in nomnoml
    assert "[C] <--> [D]" in nomnoml
    assert "[D] +-> [E]" in nomnoml
    assert "[E] o-> [F]" in nomnoml
    assert "[F] --:> [G]" in nomnoml
    assert "[G] <:-- [H]" in nomnoml
    assert "[H] -- [I]" in nomnoml


def test_parse_text_description_keywords():
    text = """
    Order contains OrderItem
    Company aggregates Employee
    Client uses Service
    Frontend calls Backend
    Service relates to Database
    """
    nomnoml = parse_text_description(text)
    assert "[Order] +-> [OrderItem]" in nomnoml
    assert "[Company] o-> [Employee]" in nomnoml
    assert "[Client] -> [Service]" in nomnoml
    assert "[Frontend] -> [Backend]" in nomnoml
    assert "[Service] - [Database]" in nomnoml


def test_parse_text_description_directives_and_comments():
    text = """
    #stroke: #222
    // this is a comment
    A -> B
    """
    nomnoml = parse_text_description(text, title="System Architecture", direction="right")
    assert "#title: System Architecture" in nomnoml
    assert "#direction: right" in nomnoml
    assert "#stroke: #222" in nomnoml
    assert "// this is a comment" in nomnoml
    assert "[A] -> [B]" in nomnoml


def test_parse_text_description_compartments():
    text = "Account | balance: float | deposit(); withdraw()"
    nomnoml = parse_text_description(text)
    assert "[Account|balance: float|deposit(); withdraw()]" in nomnoml


def test_parse_text_description_already_bracketed():
    text = "[nomnoml] is -> [awesome]"
    nomnoml = parse_text_description(text)
    assert "[nomnoml] is -> [awesome]" in nomnoml


def test_get_kroki_url():
    diagram = "[User] -> [Database]"
    url = get_kroki_url(diagram, output_format="svg", server_url="https://kroki.example.com")
    assert url.startswith("https://kroki.example.com/nomnoml/svg/")
    encoded = url.split("/")[-1]
    decoded = zlib.decompress(base64.urlsafe_b64decode(encoded.encode("ascii"))).decode("utf-8")
    assert decoded == diagram


def test_render_nomnoml_mocked():
    diagram = "[A] -> [B]"
    fake_svg = b"<svg>test</svg>"

    with mock.patch("requests.post") as mock_post:
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.content = fake_svg
        mock_response.raise_for_status = mock.Mock()
        mock_post.return_value = mock_response

        res = render_nomnoml(diagram, output_format="svg")
        assert res == fake_svg
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://kroki.io/nomnoml/svg"
        assert kwargs["data"] == diagram.encode("utf-8")
        assert kwargs["headers"]["Content-Type"] == "text/plain; charset=utf-8"


def test_render_nomnoml_error_handling():
    with mock.patch("requests.post") as mock_post:
        mock_response = mock.Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.HTTPError("Bad Request")
        mock_post.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            render_nomnoml("invalid syntax")
