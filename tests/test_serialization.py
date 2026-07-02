from src.word_engine import Word, letter_to_symbol, symbol_to_letter


def test_letter_symbols_roundtrip():
    for letter in [1, -1, 8, -8]:
        assert symbol_to_letter(letter_to_symbol(letter)) == letter


def test_four_bit_codes_and_hex():
    word = Word([2, -3, 8, -7])
    assert word.to_codes() == [2, 5, 14, 13]
    assert word.to_hex() == "25ed"
    assert word.bit_size() == 16
