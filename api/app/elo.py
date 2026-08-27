"""Plain Elo rating maths (K-factor 20).

Kept as pure functions with no DB access so the symmetry acceptance
criterion can be unit-tested deterministically.
"""

K_FACTOR = 20


def expected_score(rating: int, opponent_rating: int) -> float:
    """Expected score of `rating` against `opponent_rating` (Elo logistic)."""
    return 1.0 / (1.0 + 10 ** ((opponent_rating - rating) / 400.0))


def new_ratings(white: int, black: int, result: str) -> tuple[int, int]:
    """Return (new_white, new_black) after a game.

    result is '1-0' (white wins), '0-1' (black wins), or '1/2-1/2' (draw).
    Symmetry: the two deltas sum to zero before rounding.
    """
    if result == "1-0":
        s_white, s_black = 1.0, 0.0
    elif result == "0-1":
        s_white, s_black = 0.0, 1.0
    elif result == "1/2-1/2":
        s_white, s_black = 0.5, 0.5
    else:
        raise ValueError(f"invalid result: {result!r}")

    e_white = expected_score(white, black)
    e_black = expected_score(black, white)

    new_white = white + round(K_FACTOR * (s_white - e_white))
    new_black = black + round(K_FACTOR * (s_black - e_black))
    return new_white, new_black
