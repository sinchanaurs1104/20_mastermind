from collections import Counter


def feedback(code, guess):
    """Return (exact, partial) for a guess against a secret code.

    exact   -> symbols that are correct AND in the correct position.
    partial -> symbols that exist in the code but are in the wrong position.

    Every position in the code (and in the guess) is counted at most once,
    so repeated symbols never inflate the feedback. Exact matches are
    resolved first; only the leftovers are considered for partial matches.
    """
    if len(code) != len(guess):
        raise ValueError("code and guess must have the same length")

    exact = 0
    unmatched_code = []    # code symbols NOT claimed by an exact match
    unmatched_guess = []   # guess symbols NOT claimed by an exact match

    # Pass 1: exact matches. A matched position is consumed on both sides.
    for c, g in zip(code, guess):
        if c == g:
            exact += 1
        else:
            unmatched_code.append(c)
            unmatched_guess.append(g)

    # Pass 2: partial matches, using only the leftover symbols.
    # min() of the two counts = how many times that symbol can be paired
    # up, so one code occurrence is never reused.
    code_counts = Counter(unmatched_code)
    guess_counts = Counter(unmatched_guess)
    partial = sum(min(code_counts[s], guess_counts[s]) for s in guess_counts)

    return exact, partial
