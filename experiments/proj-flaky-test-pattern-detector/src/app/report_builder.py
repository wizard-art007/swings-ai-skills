from app.analyzer import analyze_flaky_runs
from app.diagrammer import generate_sequence_diagram, generate_retry_sequence_diagram


def build_flaky_report(runs, events=None):
    """
    Produce an integrated diagnostic markdown report containing flakiness metrics
    and embedded sequence diagrams.

    Args:
        runs (list[dict]): List of test execution run records.
        events (list[dict] | dict, optional): Sequence of interaction events or dict of events per test.

    Returns:
        str: Integrated diagnostic markdown report.
    """
    if runs is None:
        runs = []

    analysis = analyze_flaky_runs(runs)

    flaky_tests = analysis.get('flaky_tests', {})
    non_flaky_tests = analysis.get('non_flaky_tests', {})
    cov_delta = analysis.get('coverage_delta', {})
    total_runs = analysis.get('total_runs', 0)
    total_tests = analysis.get('total_tests', 0)

    lines = []
    lines.append("# Flaky Test Diagnostic Report")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append(f"- **Total Tests Analyzed**: {total_tests}")
    lines.append(f"- **Total Execution Runs**: {total_runs}")
    lines.append(f"- **Flaky Tests Detected**: {len(flaky_tests)}")
    lines.append(f"- **Coverage Delta**: {cov_delta}")
    lines.append("")

    lines.append("## Flaky Test Details")
    if flaky_tests:
        for name, details in flaky_tests.items():
            rate = details.get('flakiness_rate', 0.0)
            rate_str = f"{rate * 100:.1f}%"
            passed = details.get('passed_count', 0)
            failed = details.get('failed_count', 0)
            total = details.get('total_runs', 0)
            lines.append(f"### {name}")
            lines.append(f"- **Flakiness Rate**: {rate_str}")
            lines.append(f"- **Total Runs**: {total} (Passed: {passed}, Failed: {failed})")
            lines.append("")
    else:
        lines.append("No flaky tests detected.")
        lines.append("")

    lines.append("## Non-Flaky Test Details")
    if non_flaky_tests:
        for name, details in non_flaky_tests.items():
            passed = details.get('passed_count', 0)
            failed = details.get('failed_count', 0)
            total = details.get('total_runs', 0)
            lines.append(f"### {name}")
            lines.append(f"- **Total Runs**: {total} (Passed: {passed}, Failed: {failed})")
            lines.append("")
    else:
        lines.append("No non-flaky tests recorded.")
        lines.append("")

    lines.append("## Sequence Diagrams")

    diagrams = []

    if events:
        if isinstance(events, list):
            diag = generate_sequence_diagram(events, title="Interaction Sequence Trace")
            diagrams.append(diag)
        elif isinstance(events, dict):
            for t_name, t_events in events.items():
                if isinstance(t_events, list):
                    diag = generate_sequence_diagram(t_events, title=f"Sequence Trace: {t_name}")
                    diagrams.append(diag)
    else:
        if flaky_tests:
            for t_name, details in flaky_tests.items():
                t_runs = details.get('runs', [])
                diag = generate_retry_sequence_diagram(t_name, t_runs)
                diagrams.append(diag)
        else:
            diag = generate_sequence_diagram([], title="Default Sequence Diagram")
            diagrams.append(diag)

    for diag in diagrams:
        lines.append("```plantuml")
        lines.append(diag)
        lines.append("```")
        lines.append("")

    return "\n".join(lines)
