from src.word_engine import Word, deterministic_word, pseudo_anosov_biased_word


def test_free_reduction_and_inverse():
    word = Word([1, -1, 2, 3, -3])
    assert word.letters == (2,)
    assert (word * word.inverse()).letters == ()


def test_power_and_conjugation():
    a = Word([1, 2])
    h = Word([3])
    assert a.power(3).letters == (1, 2, 1, 2, 1, 2)
    assert a.conjugate_by(h).letters == (3, 1, 2, -3)


def test_sampling_is_deterministic():
    assert deterministic_word("seed", 10) == deterministic_word("seed", 10)
    assert pseudo_anosov_biased_word("seed", 10) == pseudo_anosov_biased_word("seed", 10)
