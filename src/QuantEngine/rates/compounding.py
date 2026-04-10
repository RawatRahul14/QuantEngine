# === Python Packages ===
import numpy as np
from typing import List, Literal

# === Function to calculate compound interest with m (number of payments in a year) ===
def calculate_compound_interest(
        principal: float,
        rate: float,
        years: float | int,
        payments_per_year: int
) -> float:
    """
    Calculates the future value of an investment using discrete compounding.
    This function implements the standard formula: V = P * (1 + r/m)^(m*t)

    Args:
        principal (float): The initial amount of money being invested (P).
        rate (float): The annual interest rate as a decimal (e.g., 0.05 for 5%).
        years (float | int): The duration of the investment in years (t).
        payments_per_year (int): The number of times interest is compounded per year (m). Common values: 1 (annual), 2 (semi-annual), 4 (quarterly), 12 (monthly).

    Returns:
        future_value (float): The total value of the investment at the end of the specified period.
    """
    ## === Validation if all the necessary variables are provided ===
    missing: List = []

    ## === Adding the names of all the missing variables ===
    if principal is None:
        missing.append("principal")
    if rate is None:
        missing.append("rate")
    if years is None:
        missing.append("years")
    if payments_per_year is None:
        missing.append("payments_per_year")

    if len(missing) > 0:
        raise ValueError(f"There are missing variables: {missing}")

    ## === Mathematical Sanity Checks ===
    if principal <= 0:
        raise ValueError("principal must be greater than 0 to avoid division by zero.")

    if payments_per_year <= 0:
        raise ValueError("payments_per_year must be greater than 0 to avoid division by zero.")

    if rate <= 0:
        raise ValueError("rate must be greater than 0 to avoid division by zero.")

    if years <= 0:
        raise ValueError("years must be greater than 0 to avoid division by zero.")

    ## === Calculation ===
    future_value = round(principal * (1 + rate / payments_per_year) ** (payments_per_year * years), 2)

    return float(future_value)

# === Function to calculate continuous compounding interest ===
def calculate_continuous_interest(
        principal: float,
        rate: float,
        years: float | int
) -> float:
    """
    Calculates the future value of an investment using continuous compounding.
    This function implements the formula: V = P * e^(r*t)

    Args:
        principal (float): The initial amount of money being invested (P).
        rate (float): The annual interest rate as a decimal (e.g., 0.05 for 5%).
        years (float | int): The duration of the investment in years (t).

    Returns:
        future_value (float): The total value of the investment at the end of the specified period.
    """
    ## === Validation if all the necessary variables are provided ===
    missing: List = []

    ## === Adding the names of all the missing variables ===
    if principal is None:
        missing.append("principal")
    if rate is None:
        missing.append("rate")
    if years is None:
        missing.append("years")

    if len(missing) > 0:
        raise ValueError(f"There are missing variables: {missing}")

    ## === Mathematical Sanity Checks ===
    if principal <= 0:
        raise ValueError("principal must be greater than 0 to avoid division by zero.")

    if rate <= 0:
        raise ValueError("rate must be greater than 0 to avoid division by zero.")

    if years <= 0:
        raise ValueError("years must be greater than 0 to avoid division by zero.")

    ## === Calculation ===
    # Using np.exp for e^(r*t)
    future_value = round(principal * np.exp(rate * years), 2)

    return float(future_value)

def convert_coumpounding_frequency(
        rate_original: float,
        m_original: int,
        m_target: int
) -> float:
    """
    Converts an interest rate from one compounding frequency to another.

    Args:
        rate_original (float): The interest rate with the original frequency (Rm1).
        m_original (int): The original number of payments per year (m1).
        m_target (int): The target number of payments per year (m2).

    Returns:
        rate_target (float): The equivalent interest rate for the target frequency (Rm2).
    """
    ## === Validation if all the necessary variables are provided ===
    missing: List = []

    if rate_original is None:
        missing.append("rate_original")
    if m_original is None:
        missing.append("m_original")
    if m_target is None:
        missing.append("m_target")

    if len(missing) > 0:
        raise ValueError(f"There are missing variables: {missing}")

    ## === Mathematical Sanity Checks ===
    if rate_original <= 0:
        raise ValueError("rate_original must be greater than 0.")

    if m_original <= 0 or m_target <= 0:
        raise ValueError("Compounding frequencies (m) must be greater than 0.")
    
    ## === Calculations ===
    rate_target = m_target * (((1 + (rate_original / m_original)) ** (m_original / m_target)) - 1)

    return round(rate_target, 5)

# === Function to convert between continuous and discrete compounding rates ===
def convert_rate_convention(
        rate: float,
        payments_per_year: int,
        convert_to: Literal["continuous", "discrete"] = "continuous"
) -> float:
    """
    Converts an interest rate between discrete and continuous compounding conventions.

    Conversions:
    - Discrete to Continuous: Rc = m * ln(1 + Rm/m)
    - Continuous to Discrete: Rm = m * (exp(Rc/m) - 1)

    Args:
        rate (float): The interest rate to be converted (as a decimal).
        payments_per_year (int): Compounding frequency per year (m).
        convert_to (Literal["continuous", "discrete"]): The target convention. Use "continuous" or "discrete".

    Returns:
        converted_rate (float): The equivalent rate in the target convention.
    """
    ## === Validation if all the necessary variables are provided ===
    missing: List = []

    if rate is None:
        missing.append("rate")
    if payments_per_year is None:
        missing.append("payments_per_year")
    if convert_to is None:
        missing.append("convert_to")

    if len(missing) > 0:
        raise ValueError(f"There are missing variables: {missing}")

    ## === Mathematical Sanity Checks ===
    if rate <= 0:
        raise ValueError("rate must be greater than 0.")

    if payments_per_year <= 0:
        raise ValueError("payments_per_year must be greater than 0.")

    ## === Calculations ===
    if convert_to.lower() == "continuous":
        # Converting Discrete (Rm) -> Continuous (Rc)
        converted_rate = payments_per_year * np.log(1 + rate / payments_per_year)

    elif convert_to.lower() == "discrete":
        # Converting Continuous (Rc) -> Discrete (Rm)
        converted_rate = payments_per_year * (np.exp(rate / payments_per_year) - 1)

    else:
        raise ValueError("convert_to must be either 'continuous' or 'discrete'.")

    return float(round(converted_rate, 5))