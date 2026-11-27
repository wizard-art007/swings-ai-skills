import os
import re
import sys
import argparse
from datetime import datetime, timedelta

DATE_FORMAT = "%Y-%m-%d"

def parse_frontmatter(content):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content
    fm_raw, body = match.groups()
    meta = {}
    for line in fm_raw.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip('"\'')
    return meta, body

def serialize_frontmatter(meta, body):
    lines = ["---"]
    for k, v in meta.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append(body)
    return "\n".join(lines)

def calculate_sm2(quality, repetitions, interval, ease_factor):
    """SuperMemo SM-2 algorithm implementation."""
    if quality >= 3:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetitions += 1
    else:
        repetitions = 0
        interval = 1

    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ease_factor < 1.3:
        ease_factor = 1.3

    return repetitions, interval, round(ease_factor, 2)

def process_card_file(filepath, quality=None):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    meta, body = parse_frontmatter(content)
    if meta.get("card", "").lower() != "true":
        return None

    today = datetime.now().date()
    due_date_str = meta.get("due_date", today.strftime(DATE_FORMAT))
    try:
        due_date = datetime.strptime(due_date_str, DATE_FORMAT).date()
    except ValueError:
        due_date = today

    if quality is not None:
        reps = int(meta.get("repetitions", 0))
        interval = int(meta.get("interval", 0))
        ef = float(meta.get("ease_factor", 2.5))

        reps, interval, ef = calculate_sm2(quality, reps, interval, ef)
        next_due = today + timedelta(days=interval)

        meta["repetitions"] = str(reps)
        meta["interval"] = str(interval)
        meta["ease_factor"] = str(ef)
        meta["due_date"] = next_due.strftime(DATE_FORMAT)

        new_content = serialize_frontmatter(meta, body)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

    return {
        "filepath": filepath,
        "body": body.strip(),
        "due_date": due_date,
        "repetitions": int(meta.get("repetitions", 0)),
        "interval": int(meta.get("interval", 0)),
        "ease_factor": float(meta.get("ease_factor", 2.5))
    }

def scan_directory(directory):
    cards = []
    if not os.path.exists(directory):
        return cards
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                path = os.path.join(root, file)
                card = process_card_file(path)
                if card:
                    cards.append(card)
    return cards

def main():
    parser = argparse.ArgumentParser(description="Olumino Markdown Spaced Repetition CLI")
    subparsers = parser.add_subparsers(dest="command")

    rev_parser = subparsers.add_parser("review", help="Review due flashcards")
    rev_parser.add_argument("--dir", required=True, help="Directory containing markdown notes")

    args = parser.parse_args()
    if args.command == "review":
        cards = scan_directory(args.dir)
        today = datetime.now().date()
        due_cards = [c for c in cards if c["due_date"] <= today]

        if not due_cards:
            print("No cards due for review today!")
            return

        print(f"Found {len(due_cards)} cards due for review.")
        for card in due_cards:
            print("\n" + "="*40)
            print(f"File: {card['filepath']}")
            print(f"Question/Front:\n{card['body']}")
            print("="*40)
            q = input("Rate quality (0-5, or q to quit): ")
            if q.lower() == 'q':
                break
            try:
                rating = int(q)
                if 0 <= rating <= 5:
                    process_card_file(card['filepath'], quality=rating)
                    print(f"Card updated! Next interval: {card['interval']} days.")
                else:
                    print("Rating must be between 0 and 5.")
            except ValueError:
                print("Invalid input, skipping.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
