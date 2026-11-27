import os
import sys
import pytest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import olumino

def test_frontmatter_parsing():
    content = """---
card: true
due_date: 2026-01-01
interval: 1
repetitions: 0
ease_factor: 2.5
---
What is the capital of France?
"""
    meta, body = olumino.parse_frontmatter(content)
    assert meta["card"] == "true"
    assert meta["due_date"] == "2026-01-01"
    assert "capital of France" in body

def test_sm2_algorithm():
    # Quality 4 (good response) on new card
    reps, interval, ef = olumino.calculate_sm2(4, 0, 0, 2.5)
    assert reps == 1
    assert interval == 1
    assert ef >= 1.3

    # Quality 4 on second repetition
    reps, interval, ef = olumino.calculate_sm2(4, 1, 1, 2.5)
    assert reps == 2
    assert interval == 6

def test_directory_scan_and_review(tmp_path):
    note_dir = tmp_path / "notes"
    note_dir.mkdir()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    note_file = note_dir / "card1.md"
    note_file.write_text(f"""---
card: true
due_date: {today_str}
interval: 0
repetitions: 0
ease_factor: 2.5
---
Test Question?
""", encoding="utf-8")

    cards = olumino.scan_directory(str(note_dir))
    assert len(cards) == 1
    assert cards[0]["repetitions"] == 0

    # Simulate review with quality 4
    olumino.process_card_file(str(note_file), quality=4)

    updated_cards = olumino.scan_directory(str(note_dir))
    assert updated_cards[0]["repetitions"] == 1
    assert updated_cards[0]["interval"] == 1
