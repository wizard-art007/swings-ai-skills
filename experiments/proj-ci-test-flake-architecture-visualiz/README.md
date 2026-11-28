# CI Test Flake & Architecture Visualizer

Detect flaky test patterns from execution logs and generate an architecture sequence flow diagram of the failing test execution path.

Built by Swings AI from its own skill tools, one milestone per session.

## Milestones

1. m1_flake_pattern_detector: Implement basic test flake detection parsing input logs for intermittent failure patterns.
2. m2_flake_sequence_visualizer: Combine flake analysis with PlantUML sequence generation to diagram the failing test interaction path.

## Skill tools used (copied into src/vendor/, with their licences)

- plantuml-plantuml/class_diagram_generator.py (sha256 9245c24bccd220a4)
- plantuml-plantuml/sequence_generator.py (sha256 0021aa8a195b04a7)
- sebastianbergmann-php-code-coverage/test_coverage_analyzer.py (sha256 6e52a46c4b8bedde)
