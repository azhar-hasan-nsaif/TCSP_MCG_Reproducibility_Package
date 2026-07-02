"""Deterministic signed-generator word engine for reproducibility.

This module is intentionally a symbolic signed-word model. It implements the
serialization and free-reduction rules used by the artifact, not a certified
complete computational mapping-class-group normal form.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random
from typing import Iterable


R0 = 8
C_PK = 4


def validate_letter(letter: int, r0: int = R0) -> int:
    """Validate a signed-generator letter encoded as +/-1 through +/-r0."""

    if not isinstance(letter, int) or letter == 0 or abs(letter) > r0:
        raise ValueError(f"letter must be one of +/-1..+/-{r0}")
    return letter


def letter_to_symbol(letter: int) -> str:
    """Convert an integer signed-generator letter to a stable textual symbol."""

    validate_letter(letter)
    return f"g{letter}" if letter > 0 else f"g{-letter}^-1"


def symbol_to_letter(symbol: str) -> int:
    """Parse a stable textual generator symbol."""

    if not symbol.startswith("g"):
        raise ValueError(f"invalid generator symbol: {symbol}")
    if symbol.endswith("^-1"):
        return -validate_letter(int(symbol[1:-3]))
    return validate_letter(int(symbol[1:]))


def reduce_letters(letters: Iterable[int]) -> tuple[int, ...]:
    """Apply adjacent inverse-pair cancellation deterministically."""

    stack: list[int] = []
    for letter in letters:
        value = validate_letter(letter)
        if stack and stack[-1] == -value:
            stack.pop()
        else:
            stack.append(value)
    return tuple(stack)


@dataclass(frozen=True)
class Word:
    """A free-reduced symbolic word over the signed-generator alphabet."""

    letters: tuple[int, ...]
    r0: int = R0
    c_pk: int = C_PK

    def __init__(self, letters: Iterable[int] = (), r0: int = R0, c_pk: int = C_PK):
        if r0 != R0:
            raise ValueError("this artifact fixes r0=8 for the Table 14 generator set")
        if c_pk < C_PK:
            raise ValueError("c_pk must be at least 4 bits for 16 signed symbols")
        object.__setattr__(self, "letters", reduce_letters(tuple(letters)))
        object.__setattr__(self, "r0", r0)
        object.__setattr__(self, "c_pk", c_pk)

    def __mul__(self, other: "Word") -> "Word":
        return Word(self.letters + other.letters, self.r0, self.c_pk)

    def inverse(self) -> "Word":
        return Word((-letter for letter in reversed(self.letters)), self.r0, self.c_pk)

    def power(self, exponent: int) -> "Word":
        if not isinstance(exponent, int):
            raise ValueError("exponent must be an integer")
        if exponent == 0:
            return Word((), self.r0, self.c_pk)
        if exponent < 0:
            return self.inverse().power(-exponent)
        result = Word((), self.r0, self.c_pk)
        base = self
        exp = exponent
        while exp:
            if exp & 1:
                result = result * base
            base = base * base
            exp >>= 1
        return result

    def conjugate_by(self, conjugator: "Word") -> "Word":
        return conjugator * self * conjugator.inverse()

    def serialization_length(self) -> int:
        return len(self.letters)

    def bit_size(self) -> int:
        return self.serialization_length() * self.c_pk

    def symbols(self) -> list[str]:
        return [letter_to_symbol(letter) for letter in self.letters]

    def to_string(self) -> str:
        return " ".join(self.symbols()) if self.letters else "1"

    def to_codes(self) -> list[int]:
        """Serialize each signed symbol as a deterministic 4-bit code 0..15."""

        return [((abs(letter) - 1) * 2 + (0 if letter > 0 else 1)) for letter in self.letters]

    def to_hex(self) -> str:
        """Pack 4-bit signed-symbol codes into a stable hexadecimal string."""

        return "".join(format(code, "x") for code in self.to_codes())

    def sha256(self) -> str:
        payload = ",".join(map(str, self.letters)).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


def word_from_symbols(symbols: Iterable[str]) -> Word:
    """Construct a word from stable textual generator symbols."""

    return Word(symbol_to_letter(symbol) for symbol in symbols)


def deterministic_word(seed: str, length: int, r0: int = R0) -> Word:
    """Sample a deterministic reduced word with no immediate inverse backtracking."""

    if length < 0:
        raise ValueError("length must be nonnegative")
    rng = random.Random(seed)
    letters: list[int] = []
    for _ in range(length):
        choices = [i for i in range(1, r0 + 1)] + [-i for i in range(1, r0 + 1)]
        if letters:
            choices = [value for value in choices if value != -letters[-1]]
        letters.append(rng.choice(choices))
    return Word(letters)


def pseudo_anosov_biased_word(seed: str, length: int, r0: int = R0) -> Word:
    """Deterministic pseudo-Anosov-biased sampler alternating supports.

    The rule biases samples away from repeated small supports by preferring a
    different absolute generator index than the previous letter when possible.
    It is reproducible and documented, but it is not a pseudo-Anosov certifier.
    """

    if length < 0:
        raise ValueError("length must be nonnegative")
    rng = random.Random(seed)
    letters: list[int] = []
    for position in range(length):
        abs_choices = list(range(1, r0 + 1))
        if letters:
            previous_abs = abs(letters[-1])
            abs_choices = [idx for idx in abs_choices if idx != previous_abs] or abs_choices
        index = rng.choice(abs_choices)
        sign = 1 if ((rng.getrandbits(1) + position) % 2 == 0) else -1
        candidate = sign * index
        if letters and candidate == -letters[-1]:
            candidate = -candidate
        letters.append(candidate)
    return Word(letters)
