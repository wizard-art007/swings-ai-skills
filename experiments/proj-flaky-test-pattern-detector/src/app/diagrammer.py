from vendor.plantuml_plantuml.sequence_generator import make_sequence


def generate_sequence_diagram(events, title="Sequence Diagram", autonumber=True):
    """
    Generate PlantUML sequence diagrams illustrating interaction sequences
    during test attempts and retries.

    Args:
        events (list[dict | tuple]): Sequence of interaction events.
            Each event is expected to have 'actor'/'sender', 'target'/'receiver',
            and 'message'/'msg' (or be a tuple of (actor, target, message)).
        title (str, optional): Title for the sequence diagram.
        autonumber (bool, optional): Whether to include autonumbering. Default True.

    Returns:
        str: PlantUML sequence diagram formatted string.
    """
    if events is None:
        events = []

    actors = []
    formatted_dicts = []
    formatted_tuples = []

    for ev in events:
        if isinstance(ev, dict):
            actor = str(ev.get('actor') or ev.get('sender') or ev.get('from') or 'Runner')
            target = str(ev.get('target') or ev.get('receiver') or ev.get('to') or 'API')
            msg = str(ev.get('message') or ev.get('msg') or ev.get('text') or '')
        elif isinstance(ev, (tuple, list)):
            actor = str(ev[0]) if len(ev) > 0 else 'Runner'
            target = str(ev[1]) if len(ev) > 1 else 'API'
            msg = str(ev[2]) if len(ev) > 2 else ''
        else:
            actor = 'Runner'
            target = 'API'
            msg = str(ev)

        if actor not in actors:
            actors.append(actor)
        if target not in actors:
            actors.append(target)

        formatted_dicts.append({
            'actor': actor,
            'target': target,
            'message': msg
        })
        formatted_tuples.append((actor, target, msg))

    # Try calling vendor make_sequence defensively
    try:
        puml = make_sequence(actors, events, title, autonumber)
        if puml and isinstance(puml, str) and '@startuml' in puml:
            if title and title not in puml:
                lines = puml.splitlines()
                lines.insert(1, f"title {title}")
                puml = "\n".join(lines)
            return puml
    except Exception:
        pass

    try:
        puml = make_sequence(actors, formatted_tuples, title, autonumber)
        if puml and isinstance(puml, str) and '@startuml' in puml:
            if title and title not in puml:
                lines = puml.splitlines()
                lines.insert(1, f"title {title}")
                puml = "\n".join(lines)
            return puml
    except Exception:
        pass

    try:
        puml = make_sequence(actors, formatted_dicts, title, autonumber)
        if puml and isinstance(puml, str) and '@startuml' in puml:
            if title and title not in puml:
                lines = puml.splitlines()
                lines.insert(1, f"title {title}")
                puml = "\n".join(lines)
            return puml
    except Exception:
        pass

    # Fallback sequence diagram generator if vendor call signature differs
    lines = ["@startuml"]
    if title:
        lines.append(f"title {title}")
    if autonumber:
        lines.append("autonumber")
    for actor in actors:
        lines.append(f"participant {actor}")
    for item in formatted_dicts:
        lines.append(f"{item['actor']} -> {item['target']} : {item['message']}")
    lines.append("@enduml")
    return "\n".join(lines)


def generate_retry_sequence_diagram(test_name, runs, title=None):
    """
    Generate a sequence diagram specifically for test attempt retries.

    Args:
        test_name (str): Name of the test.
        runs (list[dict]): List of run details for the test.
        title (str, optional): Custom diagram title.

    Returns:
        str: PlantUML sequence diagram string.
    """
    if title is None:
        title = f"Retry Trace: {test_name}"

    events = []
    for idx, run in enumerate(runs, 1):
        status = run.get('status', 'unknown')
        msg = f"Attempt {idx}: {status}"
        if 'error' in run:
            msg += f" ({run['error']})"
        events.append({
            'actor': 'Runner',
            'target': test_name,
            'message': msg
        })

    return generate_sequence_diagram(events, title=title)
