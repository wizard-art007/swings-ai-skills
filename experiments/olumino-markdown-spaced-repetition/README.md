# Olumino Markdown Spaced Repetition

Olumino is a lightweight offline Markdown notes and spaced repetition system inspired by modern local-first developer utilities. It parses markdown files containing frontmatter metadata for flashcard scheduling using the SuperMemo SM-2 algorithm.

## How It Works

1. **Markdown Frontmatter Parsing**: Flashcards are embedded directly inside standard Markdown notes using YAML-style frontmatter headers (e.g., `card: true`, `interval`, `repetitions`, `ease_factor`, `due_date`).
2. **SM-2 Spaced Repetition**: Each review updates the card's interval, ease factor, and next due date based on user performance ratings (0-5).
3. **CLI Interface**: Run reviews, list due cards, or ingest new markdown notes entirely offline from your terminal.

## How to Run

Ensure you have Python 3 installed.

Run the CLI tool:
