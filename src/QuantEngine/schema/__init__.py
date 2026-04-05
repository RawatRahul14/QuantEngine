# === Python Modules ===
from typing import TypedDict, Literal

# === MVHR - Sizing Schema ===
class SizingSchema(TypedDict):
    optimal_hedge_ratio: float
    contracts_to_trade: int
    direction: Literal["SHORT", "LONG", "NONE"]
    exact_contracts: float
    hedge_notional: float
    basis_point_value: float

# === MVHR - Effective Hedge Schema ===
class HedgeEffectivenessSchema(TypedDict):
    hedge_effectiveness: float
    effectiveness_rating: Literal["STRONG", "MODERATE", "WEAK", "POOR"]
    residual_risk: float