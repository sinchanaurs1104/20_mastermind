import random
from collections import namedtuple
from logic import feedback

# One difficulty = how long the code is, which symbols may appear in it,
# and how many guesses the player gets. Symbols are single digit characters.
Difficulty = namedtuple("Difficulty", "code_length symbols max_turns")

DIFFICULTIES = {
    "easy":   Difficulty(code_length=4, symbols="1234",     max_turns=12),
    "medium": Difficulty(code_length=4, symbols="123456",   max_turns=10),
    "hard":   Difficulty(code_length=5, symbols="12345678", max_turns=8),
}
DEFAULT_DIFFICULTY = "medium"


class GameOverError(Exception):
    """Raised when someone tries to change the game after it has ended."""


def describe(difficulty):
    """Human-readable one-line summary of a difficulty, e.g. for menus."""
    d = DIFFICULTIES[difficulty]
    return (f"{d.code_length} digits from {d.symbols[0]} to {d.symbols[-1]}, "
            f"{d.max_turns} guesses")


def choose_difficulty():
    """Show a menu and return a difficulty name, or None if the player quits.

    Re-asks on bad input.
    """
    names = list(DIFFICULTIES)
    by_number = {str(i): name for i, name in enumerate(names, start=1)}
    print("Choose a difficulty:")
    for number, name in by_number.items():
        print(f"  {number}. {name:<7} {describe(name)}")
    while True:
        try:
            raw = input("Difficulty (name or number, q to quit) > ").strip().lower()
        except EOFError:
            return None
        if raw == "q":
            return None
        if raw in DIFFICULTIES:
            return raw
        if raw in by_number:
            return by_number[raw]
        print(f"Please enter one of: {', '.join(names)} (or 1-{len(names)}).")


class Mastermind:
    # The only four states a game can be in.
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"
    QUIT = "quit"

    def __init__(self, code=None, difficulty=DEFAULT_DIFFICULTY, max_turns=None):
        # `code` can be passed in so tests can use a known secret.
        # `max_turns`, if given, overrides the difficulty's guess limit.
        if difficulty not in DIFFICULTIES:
            raise ValueError(f"Unknown difficulty {difficulty!r}. "
                             f"Choose from: {', '.join(DIFFICULTIES)}.")
        config = DIFFICULTIES[difficulty]
        self.difficulty = difficulty
        self.code_length = config.code_length
        self.symbols = config.symbols
        self.max_turns = config.max_turns if max_turns is None else max_turns

        if code is None:
            code = [random.choice(self.symbols) for _ in range(self.code_length)]
        self.code = list(code)
        if (len(self.code) != self.code_length
                or any(ch not in self.symbols for ch in self.code)):
            raise ValueError(f"Code {''.join(self.code)!r} does not fit the "
                             f"{difficulty!r} difficulty.")

        self.history = []          # one (guess, exact, partial) per ACCEPTED guess
        self.status = self.PLAYING

    # ---------- state (derived, so it can never drift out of sync) ----------

    @property
    def turns_left(self):
        return self.max_turns - len(self.history)

    @property
    def is_over(self):
        return self.status != self.PLAYING

    # ---------- actions ----------

    def validate(self, raw):
        """Return the guess as a list of symbols, or raise ValueError."""
        if len(raw) != self.code_length or any(ch not in self.symbols for ch in raw):
            raise ValueError(
                f"Enter exactly {self.code_length} digits from "
                f"{self.symbols[0]} to {self.symbols[-1]}."
            )
        return list(raw)

    def make_guess(self, raw):
        """Play one guess. Returns (exact, partial).

        Raises GameOverError if the game has ended, and ValueError if the
        guess is malformed. In both cases NOTHING is changed.
        """
        if self.is_over:
            raise GameOverError("The game is over.")
        guess = self.validate(raw)          # may raise -> turn not consumed

        exact, partial = feedback(self.code, guess)
        self.history.append((raw, exact, partial))

        # Win is checked BEFORE the turn limit, so a correct guess on the
        # very last turn is a win, not a loss.
        if exact == self.code_length:
            self.status = self.WON
        elif self.turns_left == 0:
            self.status = self.LOST
        return exact, partial

    def quit(self):
        """Give up. Ignored if the game has already ended."""
        if not self.is_over:
            self.status = self.QUIT

    # ---------- terminal interface ----------

    def run(self):
        print(f"Mastermind ({self.difficulty}) — enter {self.code_length} digits "
              f"from {self.symbols[0]} to {self.symbols[-1]}. "
              f"You have {self.max_turns} guesses. Type q to quit.")
        while not self.is_over:
            try:
                raw = input(f"{self.turns_left} turns left > ").strip()
            except EOFError:            # input stream closed (e.g. Ctrl-D)
                self.quit()
                break
            if raw.lower() == "q":
                self.quit()
                break
            try:
                exact, partial = self.make_guess(raw)
            except ValueError as err:
                print(err)
                continue
            print("Exact:", exact, " Partial:", partial)
        self.show_result()

    def show_result(self):
        secret = "".join(self.code)
        if self.status == self.WON:
            print(f"Cracked the code in {len(self.history)} "
                  f"guess{'es' if len(self.history) != 1 else ''}! "
                  f"The code was {secret}.")
        elif self.status == self.LOST:
            print(f"Out of turns. You lose. The code was {secret}.")
        elif self.status == self.QUIT:
            print(f"You quit. The code was {secret}.")
