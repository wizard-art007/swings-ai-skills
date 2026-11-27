# flaky_test_pattern_detector

Detect flaky test patterns from execution history, calculate coverage deltas, and generate visual sequence trace diagrams.

Built by Swings AI from its own skill tools, one milestone per session.

## Milestones

1. flaky_log_analyzer: Parse test execution logs to identify tests with inconsistent pass/fail outcomes and compute coverage deltas.
2. flaky_sequence_diagrammer: Generate PlantUML sequence diagrams illustrating interaction sequences during test attempts and retries.
3. flaky_report_generator: Produce an integrated diagnostic markdown report containing flakiness metrics and embedded sequence diagrams.

## Skill tools used (copied into src/vendor/, with their licences)

- plantuml-plantuml/class_diagram_generator.py (sha256 9245c24bccd220a4)
- plantuml-plantuml/sequence_generator.py (sha256 0021aa8a195b04a7)
- sebastianbergmann-php-code-coverage/test_coverage_analyzer.py (sha256 6e52a46c4b8bedde)
