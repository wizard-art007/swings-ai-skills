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
    formatted_events = []

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

        formatted_events.append({
            'actor': actor,
            'target': target,
            'message': msg
        })

    if not actors:
        actors = ['Runner', 'API']

    try:
        puml = make_sequence(actors, formatted_events, title, autonumber)
        if puml and isinstance(puml, str) and '@startuml' in puml:
            if title and title not in puml:
                lines = puml.splitlines()
                lines.insert(1, f"title {title}")
                puml = "\n".join(lines)
            return puml
    except Exception:
        pass

    # Fallback generator if vendor call encounters an issue
    lines = ["@startuml"]
    if title:
        lines.append(f"title {title}")
    if autonumber:
        lines.append("autonumber")
    for a in actors:
        lines.append(f"participant {a}")
    for fe in formatted_events:
        lines.append(f"{fe['actor']} -> {fe['target']}: {fe['message']}")
    lines.append("@enduml")
    return "\n".join(lines)


def generate_retry_sequence_diagram(test_name, runs, autonumber=True):
    """
    Generate a PlantUML sequence diagram specifically for test retry attempts.

    Args:
        test_name (str): Name of the test.
        runs (list): List of run dicts or attempts for the test.
        autonumber (bool, optional): Whether to enable autonumbering.

    Returns:
        str: PlantUML sequence diagram string.
    """
    title = f"Retry Trace: {test_name}"
    events = []

    if runs:
        for i, run in enumerate(runs):
            if isinstance(run, dict):
                actor = str(run.get('actor') or run.get('sender') or 'Runner')
                target = str(run.get('target') or run.get('receiver') or 'API')
                if 'message' in run or 'msg' in run:
                    msg = str(run.get('message') or run.get('msg'))
                else:
                    st = run.get('status', 'unknown')
                    err = run.get('error')
                    msg = f"Attempt {i + 1}: {st}" + (f" ({err})" if err else "")
            else:
                actor = 'Runner'
                target = 'API'
                msg = f"Attempt {i + 1}: {run}"
            events.append({'actor': actor, 'target': target, 'message': msg})
    else:
        events.append({'actor': 'Runner', 'target': 'API', 'message': 'No runs recorded'})

    return generate_sequence_diagram(events, title=title, autonumber=autonumber)
