import pytest

from src.parameters import FormulaParameters, compute_profile


def test_corrected_formulas_profile_a():
    result = compute_profile("A", FormulaParameters(lambda_q=128, lambda_c=128))
    assert result.gamma == 4
    assert result.L_min == 64
    assert result.L == 96
    assert result.genus == 70
    assert result.E == 512
    assert result.log2_T_cl == 384
    assert result.log2_T_q == 192
    assert result.public_key_bits == 1536
    assert result.secret_key_bits == 384
    assert result.ciphertext_bits == 1792


def test_invalid_inputs_raise_clear_errors():
    with pytest.raises(ValueError):
        FormulaParameters(r0=0)
    with pytest.raises(ValueError):
        FormulaParameters(alpha=1)
    with pytest.raises(ValueError):
        FormulaParameters(beta=0)
    with pytest.raises(ValueError):
        FormulaParameters(delta=1)
    with pytest.raises(ValueError):
        FormulaParameters(g0=2)
    with pytest.raises(ValueError):
        FormulaParameters(ell_mu=-1)
    with pytest.raises(ValueError):
        FormulaParameters(C_pk=3)
