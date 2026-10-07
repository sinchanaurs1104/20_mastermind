import random
from logic import feedback

CODE_LENGTH = 4
SYMBOLS = "123456"
MAX_TURNS = 10


class GameOverError(Exception):
    """Raised when someone tries to change the game after it has ended."""


class Mastermind:
    # The only four states a game can be in.
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"
    QUIT = "quit"

    def __init__(self, code=None, max_turns=MAX_TURNS):
        # `code` can be passed in so tests can use a known secret.
        if code is None:
            code = [random.choice(SYMBOLS) for _ in range(CODE_LENGTH)]
        self.code = list(code)
        self.max_turns = max_turns
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
        if len(raw) != len(self.code) or any(ch not in SYMBOLS for ch in raw):
            raise ValueError(
                f"Enter exactly {len(self.code)} digits from "
                f"{SYMBOLS[0]} to {SYMBOLS[-1]}."
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
        if exact == len(self.code):
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
        print(f"Mastermind — enter {len(self.code)} digits from "
              f"{SYMBOLS[0]} to {SYMBOLS[-1]}. Type q to quit.")
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
