"""PlantUML Sequence Diagram Generator.

Provides utility functions to construct PlantUML sequence diagram definitions
programmatically from actor and message specifications.
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

PARTICIPANT_TYPES = {
    "participant",
    "actor",
    "boundary",
    "control",
    "entity",
    "database",
    "collections",
    "queue",
}


def _format_actor(actor: Union[str, Tuple[str, ...], Dict[str, Any]]) -> str:
    """Format a single actor entry into a PlantUML participant line."""
    if isinstance(actor, str):
        cleaned = actor.strip()
        parts = cleaned.split(maxsplit=1)
        if parts and parts[0].lower() in PARTICIPANT_TYPES:
            return cleaned

        if " as " in cleaned:
            name_part, alias_part = cleaned.split(" as ", 1)
            name_part = name_part.strip()
            alias_part = alias_part.strip()
            if " " in name_part and not (name_part.startswith('"') and name_part.endswith('"')):
                name_part = f'"{name_part}"'
            return f"participant {name_part} as {alias_part}"

        if " " in cleaned and not (cleaned.startswith('"') and cleaned.endswith('"')):
            return f'participant "{cleaned}"'
        return f"participant {cleaned}"

    if isinstance(actor, (tuple, list)):
        if len(actor) == 1:
            return _format_actor(actor[0])
        if len(actor) == 2:
            first, second = actor
            if str(first).lower() in PARTICIPANT_TYPES:
                name = str(second).strip()
                if " " in name and not (name.startswith('"') and name.endswith('"')):
                    name = f'"{name}"'
                return f"{str(first).lower()} {name}"
            name = str(first).strip()
            if " " in name and not (name.startswith('"') and name.endswith('"')):
                name = f'"{name}"'
            return f"participant {name} as {second}"
        if len(actor) >= 3:
            kind, name, alias = actor[0], actor[1], actor[2]
            name_str = str(name).strip()
            if " " in name_str and not (name_str.startswith('"') and name_str.endswith('"')):
                name_str = f'"{name_str}"'
            return f"{str(kind).lower()} {name_str} as {alias}"

    if isinstance(actor, dict):
        kind = str(actor.get("type", "participant")).lower()
        name = str(actor.get("name") or actor.get("id") or "").strip()
        label = actor.get("label")
        alias = actor.get("alias")

        if label and alias:
            return f'{kind} "{label}" as {alias}'
        if alias and name:
            if " " in name and not (name.startswith('"') and name.endswith('"')):
                name = f'"{name}"'
            return f"{kind} {name} as {alias}"
        if label and name:
            return f'{kind} "{label}" as {name}'
        if name:
            if " " in name and not (name.startswith('"') and name.endswith('"')):
                name = f'"{name}"'
            return f"{kind} {name}"

    raise ValueError(f"Unsupported actor format: {actor!r}")


def _format_message(msg: Union[str, Tuple[Any, ...], Dict[str, Any]]) -> str:
    """Format a message entry into a PlantUML sequence arrow line."""
    if isinstance(msg, str):
        return msg.strip()

    if isinstance(msg, (tuple, list)):
        if len(msg) == 2:
            sender, receiver = msg
            return f"{sender} -> {receiver}"
        if len(msg) == 3:
            sender, receiver, text = msg
            return f"{sender} -> {receiver}: {text}"
        if len(msg) == 4:
            # Check if position 1 or 3 is the arrow
            if any(char in str(msg[1]) for char in ("-", ">", "<")):
                sender, arrow, receiver, text = msg
            else:
                sender, receiver, text, arrow = msg
            return f"{sender} {arrow} {receiver}: {text}"
        raise ValueError(f"Message tuple must have 2 to 4 elements, got {len(msg)}")

    if isinstance(msg, dict):
        sender = msg.get("from") or msg.get("sender") or msg.get("source")
        receiver = msg.get("to") or msg.get("receiver") or msg.get("target")
        text = msg.get("message") or msg.get("text") or msg.get("label") or msg.get("msg")
        arrow = msg.get("arrow", "->")

        if not sender or not receiver:
            raise ValueError(f"Message dict must specify sender ('from') and receiver ('to'): {msg!r}")

        if text is not None:
            return f"{sender} {arrow} {receiver}: {text}"
        return f"{sender} {arrow} {receiver}"

    raise ValueError(f"Unsupported message format: {msg!r}")


def make_sequence(
    actors: Optional[Iterable[Any]],
    messages: Optional[Iterable[Any]],
    title: Optional[str] = None,
    autonumber: bool = False,
) -> str:
    """Generate PlantUML sequence-diagram text.

    Args:
        actors: Iterable of actor definitions (strings, tuples, or dicts).
        messages: Iterable of message definitions (strings, tuples, or dicts).
        title: Optional title for the diagram.
        autonumber: If True, adds the 'autonumber' directive.

    Returns:
        PlantUML diagram string bounded by @startuml and @enduml.
    """
    lines: List[str] = ["@startuml"]

    if title:
        lines.append(f"title {title}")

    if autonumber:
        lines.append("autonumber")

    if actors:
        if isinstance(actors, dict):
            for name, kind in actors.items():
                lines.append(f"{kind} {name}")
        else:
            for actor in actors:
                lines.append(_format_actor(actor))

    if messages:
        for msg in messages:
            lines.append(_format_message(msg))

    lines.append("@enduml")
    return "\n".join(lines)


if __name__ == "__main__":
    sample_actors = ["Alice", "Bob"]
    sample_messages = [("Alice", "Bob", "Hello"), ("Bob", "Alice", "Hi back", "-->")]
    print(make_sequence(sample_actors, sample_messages, title="Greeting Flow", autonumber=True))
