"""Validated parameters and corrected Table 14 formulas."""

from __future__ import annotations

from math import ceil, log2
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


PROFILE_NAMES = ("A", "B", "C")
TABLE14_COLUMNS = [
    "Profile",
    "Nominal PQ target lambda_q",
    "L",
    "Genus g = ceil(g0 + beta L)",
    "E bits, not serialized",
    "log2 T_cl",
    "log2 T_q",
    "Public key bits",
    "Secret key bits",
    "Ciphertext bits",
]


class FormulaParameters(BaseModel):
    """Input parameters for the corrected TCSP-MCG Table 14 model."""

    model_config = ConfigDict(frozen=True)

    r0: int = Field(default=8)
    alpha: float = Field(default=1.5)
    beta: float = Field(default=2 / 3)
    delta: float = Field(default=2.0)
    g0: int = Field(default=6)
    C_pk: int = Field(default=4)
    lambda_q: int = Field(default=128)
    lambda_c: int | None = Field(default=None)
    m_b: int = Field(default=256)
    ell_mu: int = Field(default=256)
    L_override: int | None = Field(default=None)
    s_E: int = Field(default=0)

    @field_validator("r0", "C_pk")
    @classmethod
    def positive_integer(cls, value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("value must be a positive integer")
        return value

    @field_validator("lambda_q")
    @classmethod
    def positive_lambda(cls, value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("lambda_q must be a positive integer")
        return value

    @field_validator("m_b", "ell_mu", "s_E")
    @classmethod
    def nonnegative_integer(cls, value: int) -> int:
        if not isinstance(value, int) or value < 0:
            raise ValueError("value must be a nonnegative integer")
        return value

    @field_validator("L_override")
    @classmethod
    def optional_positive_integer(cls, value: int | None) -> int | None:
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("L_override must be a positive integer when supplied")
        return value

    @field_validator("lambda_c")
    @classmethod
    def optional_positive_lambda(cls, value: int | None) -> int | None:
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("lambda_c must be a positive integer when supplied")
        return value

    @model_validator(mode="after")
    def validate_ranges(self) -> "FormulaParameters":
        if self.alpha <= 1:
            raise ValueError("alpha must be greater than 1")
        if self.beta <= 0:
            raise ValueError("beta must be greater than 0")
        if self.delta <= 1:
            raise ValueError("delta must be greater than 1")
        if self.g0 < 3:
            raise ValueError("g0 must be at least 3")
        expected_cpk = ceil(log2(2 * self.r0))
        if self.C_pk < expected_cpk:
            raise ValueError(
                f"C_pk={self.C_pk} cannot encode 2*r0={2*self.r0} signed symbols; "
                f"minimum is {expected_cpk}"
            )
        return self

    @property
    def classical_target(self) -> int:
        return self.lambda_q if self.lambda_c is None else self.lambda_c

    @property
    def security_target_for_L(self) -> int:
        return max(self.classical_target, 2 * self.lambda_q)


class ProfileResult(BaseModel):
    """Computed formula outputs for a single profile."""

    model_config = ConfigDict(frozen=True)

    profile: Literal["A", "B", "C"] | str
    params: FormulaParameters
    gamma: float
    L_min: float
    L: int
    genus: int
    E: int
    ell_pk: int
    log2_T_cl: float
    log2_T_q: float
    public_key_bits: int
    secret_key_bits: int
    ciphertext_bits: int
    E_serialized: bool = False

    def table14_row(self) -> dict[str, int | str]:
        return {
            "Profile": self.profile,
            "Nominal PQ target lambda_q": self.params.lambda_q,
            "L": self.L,
            "Genus g = ceil(g0 + beta L)": self.genus,
            "E bits, not serialized": self.E,
            "log2 T_cl": int(self.log2_T_cl),
            "log2 T_q": int(self.log2_T_q),
            "Public key bits": self.public_key_bits,
            "Secret key bits": self.secret_key_bits,
            "Ciphertext bits": self.ciphertext_bits,
        }

    def formula_breakdown_row(self) -> dict[str, int | float | str | bool]:
        return {
            "Profile": self.profile,
            "r0": self.params.r0,
            "gamma = log2(2*r0)": self.gamma,
            "alpha": self.params.alpha,
            "beta": self.params.beta,
            "delta": self.params.delta,
            "g0": self.params.g0,
            "C_pk": self.params.C_pk,
            "lambda_c": self.params.classical_target,
            "lambda_q": self.params.lambda_q,
            "max(lambda_c, 2lambda_q)": self.params.security_target_for_L,
            "L_min": self.L_min,
            "L": self.L,
            "ell_pk = 2L": self.ell_pk,
            "m_b raw plaintext bits": self.params.m_b,
            "ell_mu encoded generator slots": self.params.ell_mu,
            "s_E optional extension bits": self.params.s_E,
            "E": self.E,
            "E serialized": self.E_serialized,
            "pk bits = 4LC_pk": self.public_key_bits,
            "sk bits = LC_pk": self.secret_key_bits,
            "ciphertext bits = (2L+ell_mu)C_pk+s_E": self.ciphertext_bits,
        }


def compute_profile(profile: str, params: FormulaParameters) -> ProfileResult:
    """Compute all corrected formulas for one profile."""

    if profile not in PROFILE_NAMES:
        raise ValueError(f"profile must be one of {PROFILE_NAMES}")
    gamma = log2(2 * params.r0)
    L_min = params.security_target_for_L / gamma
    L = params.L_override if params.L_override is not None else ceil(params.alpha * L_min)
    if L <= 0:
        raise ValueError("L must be positive")
    genus = ceil(params.g0 + params.beta * L)
    E = ceil(params.delta * params.security_target_for_L)
    if E < 0:
        raise ValueError("E must be nonnegative")
    ell_pk = 2 * L
    log2_T_cl = gamma * L
    log2_T_q = gamma * L / 2
    public_key_bits = 4 * L * params.C_pk
    secret_key_bits = L * params.C_pk
    ciphertext_bits = (2 * L + params.ell_mu) * params.C_pk + params.s_E
    return ProfileResult(
        profile=profile,
        params=params,
        gamma=gamma,
        L_min=L_min,
        L=L,
        genus=genus,
        E=E,
        ell_pk=ell_pk,
        log2_T_cl=log2_T_cl,
        log2_T_q=log2_T_q,
        public_key_bits=public_key_bits,
        secret_key_bits=secret_key_bits,
        ciphertext_bits=ciphertext_bits,
        E_serialized=False,
    )


def default_profile_parameters() -> dict[str, FormulaParameters]:
    """Return the manuscript's corrected representative profile inputs."""

    return {
        "A": FormulaParameters(lambda_q=128, lambda_c=128),
        "B": FormulaParameters(lambda_q=192, lambda_c=192),
        "C": FormulaParameters(lambda_q=256, lambda_c=256),
    }


def compute_table14_profiles() -> list[ProfileResult]:
    """Compute Profile A, B, and C under the corrected Table 14 convention."""

    return [
        compute_profile(profile, params)
        for profile, params in default_profile_parameters().items()
    ]
