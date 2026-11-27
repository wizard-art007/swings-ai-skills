import sys
import time

class VimTrainerGame:
    def __init__(self, initial_text="hello vim world", target_text="hello vim masters"):
        self.text = list(initial_text)
        self.target = list(target_text)
        self.cursor = 0
        self.mode = "NORMAL"  # NORMAL or INSERT
        self.history = []
        self.start_time = time.time()
        self.keystrokes = 0

    def render(self):
        txt_display = "".join(self.text)
        cursor_display = " " * self.cursor + "^"
        output = [
            f"Mode: [{self.mode}] | Keystrokes: {self.keystrokes}",
            f"Target: {''.join(self.target)}",
            f"Current: {txt_display}",
            f"         {cursor_display}",
            "Commands: h/l (move), w/b (word), i (insert), x (delete char), ESC (normal), q (quit)"
        ]
        return "\n".join(output)

    def handle_key(self, key):
        self.keystrokes += 1
        if key == 'q':
            return "QUIT"
        
        if self.mode == "INSERT":
            if key == '\x1b':  # ESC key
                self.mode = "NORMAL"
            elif key == '\x7f' or key == '\b':  # Backspace
                if self.cursor > 0:
                    self.text.pop(self.cursor - 1)
                    self.cursor -= 1
            else:
                self.text.insert(self.cursor, key)
                self.cursor += 1
        else:  # NORMAL mode
            if key == 'h':
                self.cursor = max(0, self.cursor - 1)
            elif key == 'l':
                self.cursor = min(max(0, len(self.text) - 1), self.cursor + 1)
            elif key == 'i':
                self.mode = "INSERT"
            elif key == 'x':
                if self.text and self.cursor < len(self.text):
                    self.text.pop(self.cursor)
                    self.cursor = min(self.cursor, max(0, len(self.text) - 1))
            elif key == 'w':
                # simple word jump forward
                while self.cursor < len(self.text) - 1 and self.text[self.cursor] != ' ':
                    self.cursor += 1
                while self.cursor < len(self.text) - 1 and self.text[self.cursor] == ' ':
                    self.cursor += 1
            elif key == 'b':
                # simple word jump backward
                while self.cursor > 0 and self.text[self.cursor - 1] == ' ':
                    self.cursor -= 1
                while self.cursor > 0 and self.text[self.cursor - 1] != ' ':
                    self.cursor -= 1

        if self.text == self.target:
            return "WON"
        return "CONTINUE"

def main():
    game = VimTrainerGame()
    print("Welcome to Vim Motions Trainer!")
    while True:
        print("\n" + game.render())
        sys.stdout.write("Enter key: ")
        sys.stdout.flush()
        key = sys.stdin.read(1)
        if not key:
            break
        status = game.handle_key(key)
        if status == "QUIT":
            print("\nExiting trainer.")
            break
        elif status == "WON":
            print(f"\nCongratulations! You matched the target in {game.keystrokes} keystrokes!")
            break

if __name__ == "__main__":
    main()
