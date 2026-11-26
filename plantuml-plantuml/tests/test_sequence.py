import sys
import pytest

sys.path.insert(0, "scripts")

from sequence_generator import make_sequence


def test_basic_sequence():
    actors = ["Alice", "Bob"]
    messages = [("Alice", "Bob", "Hello"), ("Bob", "Alice", "Hi")]
    diagram = make_sequence(actors, messages)

    expected = (
        "@startuml\n"
        "participant Alice\n"
        "participant Bob\n"
        "Alice -> Bob: Hello\n"
        "Bob -> Alice: Hi\n"
        "@enduml"
    )
    assert diagram == expected


def test_actors_with_spaces():
    actors = ["Web Browser", "API Gateway"]
    messages = [("Web Browser", "API Gateway", "GET /items")]
    diagram = make_sequence(actors, messages)

    assert 'participant "Web Browser"' in diagram
    assert 'participant "API Gateway"' in diagram
    assert "Web Browser -> API Gateway: GET /items" in diagram


def test_actor_types_and_aliases():
    actors = [
        "actor User",
        ("database", "DB"),
        ("queue", "Message Broker", "MB"),
        {"name": "auth", "type": "control", "alias": "AuthService"},
    ]
    messages = [
        ("User", "AuthService", "Authenticate"),
        ("AuthService", "DB", "Query user"),
    ]
    diagram = make_sequence(actors, messages)

    assert "actor User" in diagram
    assert "database DB" in diagram
    assert 'queue "Message Broker" as MB' in diagram
    assert "control auth as AuthService" in diagram
    assert "User -> AuthService: Authenticate" in diagram


def test_arrow_variations():
    actors = ["Client", "Server"]
    messages = [
        ("Client", "Server", "Request", "->"),
        ("Server", "Client", "Response", "-->"),
        ("Client", "-->", "Server", "Ack"),
        ("Client", "Server"),
    ]
    diagram = make_sequence(actors, messages)

    assert "Client -> Server: Request" in diagram
    assert "Server --> Client: Response" in diagram
    assert "Client --> Server: Ack" in diagram
    assert "Client -> Server" in diagram


def test_dict_messages_and_dict_actors():
    actors = {"Client": "actor", "DB": "database"}
    messages = [
        {"from": "Client", "to": "DB", "text": "SELECT 1", "arrow": "->"},
        {"sender": "DB", "receiver": "Client", "message": "OK", "arrow": "-->"},
    ]
    diagram = make_sequence(actors, messages)

    assert "actor Client" in diagram
    assert "database DB" in diagram
    assert "Client -> DB: SELECT 1" in diagram
    assert "DB --> Client: OK" in diagram


def test_title_and_autonumber():
    diagram = make_sequence(["A", "B"], [("A", "B", "Ping")], title="Heartbeat", autonumber=True)

    assert diagram.startswith("@startuml\ntitle Heartbeat\nautonumber\n")
    assert diagram.endswith("@enduml")


def test_empty_diagram():
    diagram = make_sequence([], [])
    assert diagram == "@startuml\n@enduml"

    diagram_none = make_sequence(None, None)
    assert diagram_none == "@startuml\n@enduml"


def test_raw_string_messages():
    actors = ["Alice", "Bob"]
    messages = [
        "Alice -> Bob: Request",
        "note right of Bob: Processing",
        "Bob --> Alice: Response",
    ]
    diagram = make_sequence(actors, messages)

    assert "note right of Bob: Processing" in diagram
    assert "Alice -> Bob: Request" in diagram


def test_invalid_actor_format():
    with pytest.raises(ValueError, match="Unsupported actor format"):
        make_sequence([12345], [])


def test_invalid_message_format():
    with pytest.raises(ValueError, match="Message tuple must have 2 to 4 elements"):
        make_sequence(["A", "B"], [("A",)])

    with pytest.raises(ValueError, match="Message dict must specify sender"):
        make_sequence(["A", "B"], [{"text": "Missing from and to"}])
