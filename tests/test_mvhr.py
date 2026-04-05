# === Python Modules ===
import pytest
import pandas as pd
import numpy as np
from QuantEngine.hedging import HedgeRatio

## === h_star test ===
def test_perfect_correlation_hedge():
    """If Spot and Futures are identical, h* should be 1.0"""
    df = pd.DataFrame({
        "spot": [100, 101, 102, 103, 104],
        "future": [100, 101, 102, 103, 104]
    })
    
    engine = HedgeRatio(
        pandas_df = df,
        spot_column_name = "spot",
        future_column_name = "future"
    )
    
    h_star = engine.get_mhvr(rounding = False)

    ## === Use approx for floating point comparisons ===
    assert h_star == pytest.approx(1.0, rel = 1e-3)

## === Sizing test ===
def test_sizing_logic():
    """
    Test if sizing returns the correct number of contracts
    """
    df = pd.DataFrame({
        "spot": [100, 101, 102, 103, 104],
        "future": [100, 101, 102, 103, 104]
    })

    engine = HedgeRatio(
        pandas_df = df,
        spot_column_name = "spot",
        future_column_name = "future"
    )

    ## === Portfolio $10,000, Futures $100, Lot Size 1, h* = 1 ===
    # Expected: 100 contracts
    res = engine.calculate_sizing(10000, 100, 1)
    assert res.get("contracts_to_trade") == 100