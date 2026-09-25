"""Small helpers shared by the game modules."""

import datetime
import math
import random
import time

# One shared random generator, so tests can seed it for repeatable results.
rng = random.Random()


def rand_int(lo, hi):
    """Random integer in [lo, hi], both ends inclusive."""
    return rng.randint(lo, hi)


def pick(seq):
    return seq[rng.randrange(len(seq))]


def roll():
    """Random float in [0, 1)."""
    return rng.random()


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def uid():
    return '%x-%010x' % (int(time.time() * 1000), rng.getrandbits(40))


def now_ms():
    return int(time.time() * 1000)


def day_number(ms):
    """The local calendar day of a timestamp in ms, as a day count (for daily rewards)."""
    return datetime.date.fromtimestamp(ms / 1000).toordinal()


def is_number(value):
    """True for int/float values (bool is deliberately excluded)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def to_int(value, default):
    """Converts save-file values to int, truncating like JavaScript's Math.trunc.

    Accepts numbers and numeric strings; anything else (or NaN/inf) gives `default`.
    """
    if isinstance(value, bool):
        return int(value)
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return int(number)


def text(value, limit):
    """Returns `value` if it is a string (trimmed to `limit` characters), else ''."""
    return value[:limit] if isinstance(value, str) else ''


def round_half_up(x):
    """Rounds like JavaScript's Math.round (Python's round() uses banker's rounding)."""
    return math.floor(x + 0.5)
