# === Python Modules ===
from typing import List, Literal
from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

# === Schema ===
from QuantEngine.schema import (
    SizingSchema,
    HedgeEffectivenessSchema
)

# === Python Class to calculate Minimum Variance Hedge Ratio ===
class HedgeRatio:
    def __init__(
            self,
            spot_column_name: str,
            future_column_name: str,
            sql_url: str | None = None,
            sql_query: str | None = None,
            pandas_df: pd.DataFrame | None = None,
            csv_data_path: str | None = None
    ):
        ## === Validate that exactly one data source is provided ===
        sources = [sql_url, pandas_df, csv_data_path]
        provided_count = sum(1 for s in sources if s is not None)

        ## === Errors ===
        if provided_count == 0:
            raise ValueError(
                "Data missing: You must provide one of [sql_url, pandas_df, csv_data_path]."
            )
        if provided_count > 1:
            raise ValueError(
                "Ambiguous Data: Multiple data sources provided. Please pass only one."
            )
        
        ## === Validating Column Names ===
        if not spot_column_name or not future_column_name:

            ## === Placeholder to store missing params ===
            missing: List[str] = []

            ## === Storing the missing variables ===
            if not spot_column_name:
                missing.append("spot_column_name")

            if not future_column_name:
                missing.append("future_column_name")

            ## === Error ===
            raise ValueError(
                "Missing column Identifiers: You must provide both 'spot_column_name' and 'future_column_name'."
                f"Missing: {missing}"
            )
        
        ## === Validating of not missing sql_query ===
        if sql_url is not None and not sql_query:
            raise ValueError(
                "SQL Configuration Error: 'sql_url' was provided, but 'sql_query' is missing."
                "The engine needs a query (e.g., 'SELECT * FROM table') to fetch data from the database."
            )

        self.spot_column_name = spot_column_name
        self.future_column_name = future_column_name

        if csv_data_path is not None:
            self.csv_data_path = csv_data_path
            self._call_csv()

        if pandas_df is not None:
            self.data = pandas_df.copy()

        if sql_url is not None:
            self.sql_url = sql_url
            self.sql_query = sql_query
            self._call_sql()

        ## === Checking whether the provided column names exist or not ===
        self._check_columns()

    def _call_csv(
        self
    ):
        """
        Calls the csv file from the given path
        """
        try:
            self.data = pd.read_csv(Path(self.csv_data_path))

        except Exception as e:
            raise ValueError("Failed to read CSV file") from e

    def _call_sql(
            self
    ):
        """
        Connects to the SQL database and fetched the required dataset.
        """
        try:
            ## === Connecting to the engine ===
            engine = create_engine(
                url = self.sql_url
            )

            ## === Fetches the Data from SQL ===
            self.data = pd.read_sql(self.sql_query, engine)

            ## === Disconnecting the engine ===
            engine.dispose()

        except Exception as e:
            raise ValueError("Failed to connect to the server.") from e

    def _check_columns(
            self
    ):
        """
        Checks whether the columns names for spot and future prices exists in the dataset or not.
        """
        existing_columns = self.data.columns

        ## === Check if both required columns exist ===
        if self.spot_column_name not in existing_columns or self.future_column_name not in existing_columns:

            missing: List[str] = []

            if self.spot_column_name not in existing_columns: 
                missing.append(self.spot_column_name)
            if self.future_column_name not in existing_columns: 
                missing.append(self.future_column_name)

            raise ValueError(
                f"Data Mapping Error: The required columns were not found in the dataset. "
                f"Missing: {missing}. Available columns: {list(existing_columns)}"
            )

    def _prepare_returns(
            self
    ):
        """
        Calculates log returns to ensure statistical stationarity.
        Log returns are preferred over simple returns for time-series additive properties.
        """
        ## === Dropping the missing values from the orginal dataset ===
        data = self.data[[self.spot_column_name, self.future_column_name]].dropna().copy()

        ## === Calculating daily log returns: ln (Pt / Pt-1) ===
        data["rets_spot"] = np.log(data[self.spot_column_name]).diff()
        data["rets_future"] = np.log(data[self.future_column_name]).diff()

        ## === Dropping NaN values ===
        self.clean_data = data.dropna(
            subset = ["rets_spot", "rets_future"]
        )

    def get_mhvr(
            self,
            rounding: bool = True,
            cross_hedge: bool = False
    ) -> float:
        """
        Calculates the Hedge Ratio based on the strategy type.

        Args:
            cross_hedge (bool): 
                - If False: Direct Hedge (Same Asset). Uses the Beta of spot vs futures.
                - If True: Cross Hedge (Different Assets). Uses Correlation * (Vol_s / Vol_f).
        """
        ## === Ensuring the resturns are calculated ===
        if not hasattr(self, "clean_data"):
            self._prepare_returns()

        ## === If there is Cross Hedging ===
        if cross_hedge:
            ## === Required Statistics ===
            std_s = self.clean_data["rets_spot"].std()
            std_f = self.clean_data["rets_future"].std()
            correlation = self.clean_data["rets_spot"].corr(self.clean_data["rets_future"])

            ## === Calculating h* ===
            h_star = correlation * (std_s / std_f)

        ## === If it's Direct Hedging ===
        else:
            cov_matrix = np.cov(
                self.clean_data["rets_spot"],
                self.clean_data["rets_future"]
            )

            ## === Calculating h_star ===
            h_star = cov_matrix[0, 1] / cov_matrix[1, 1]

        if rounding:
            return round(h_star, 4)

        else:
            return h_star

    def calculate_sizing(
            self,
            portfolio_value: float,
            current_futures_price: float,
            contract_size: int,
            cross_hedge: bool = False
    ) -> SizingSchema:
        """
        Calculates the number of contracts required to hedge the portfolio.

        Args:
            portfolio_value (float): Total value of the spot position to hedge.
            futures_price (float): Current market price of the futures contract.
            contract_size (int): Units of underlying per 1 futures contract (e.g., 65 for Nifty options).
            cross_hedge (bool): Whether to use the cross-hedge calculation for h*.
        """
        ## === Validating that current_futures_price and contract_size are positive ===
        if current_futures_price <= 0 or contract_size <= 0:
            raise ValueError(
                "Sizing Calculation Error: Futures price and contract size must be greater than zero."
            )

        ## === Calculating the optimal hedge ratio ===
        h_star = self.get_mhvr(
            rounding = False,
            cross_hedge = cross_hedge
        )

        ## === Calculate the value of one futures contract ===
        notional_per_contract = current_futures_price * contract_size

        ## === Calculate exact number of contracts ===
        ## N = h_star * (P / F)
        n_contracts_exact = h_star * (portfolio_value / notional_per_contract)

        ## === Round to nearest whole lot as you can't trade fractional contracts ===
        n_contracts_rounded = int(round(abs(n_contracts_exact)))

        ## === Direction: whether the hedging is by taking `LONG` position or `SHORT` position. ===
        if n_contracts_exact > 0:
            direction: Literal["LONG", "SHORT", "NONE"] = "SHORT"
        elif n_contracts_exact < 0:
            direction = "LONG"
        else:
            direction = "NONE"

        return SizingSchema(
            optimal_hedge_ratio = h_star,
            contracts_to_trade = n_contracts_rounded,
            direction = direction,
            exact_contracts = round(n_contracts_exact, 4),
            hedge_notional = round(n_contracts_rounded * notional_per_contract, 2),
            basis_point_value = round(notional_per_contract * 0.0001, 4)
        )

    def get_hedge_effectiveness(
            self,
            cross_hedge: bool = False
    ) -> HedgeEffectivenessSchema:
        """
        Calculates hedge effectiveness using variance reduction.
        hedge_effectiveness = 1 - Var(hedged) / Var(unhedged)
        """
        ## === Preparing the returns ===
        if not hasattr(self, "clean_data"):
            self._prepare_returns()

        ## === Required Variables ===
        spot = self.clean_data["rets_spot"]
        future = self.clean_data["rets_future"]

        ## === Getting the Hedge Ratio ===
        h_star = self.get_mhvr(
            rounding = False,
            cross_hedge = cross_hedge
        )

        ## === Hedge Returns ===
        hedged = spot - h_star * future

        ## === Variances ===
        var_unhedged = np.var(spot, ddof = 1)
        var_hedged = np.var(hedged, ddof = 1)

        ## === Error if the spot variance is 0 ===
        if var_unhedged == 0:
            raise ValueError(
                "Spot variance is zero. Cannot compute hedge effectiveness."
            )
        
        ## === Hedge Effectiveness ===
        hedge_effectiveness = 1 - (var_hedged / var_unhedged)

        ## === Interpretation ===
        status = (
            "STRONG" if hedge_effectiveness > 0.8
            else "MODERATE" if hedge_effectiveness > 0.5
            else "WEAK" if hedge_effectiveness > 0
            else "POOR"
        )

        return HedgeEffectivenessSchema(
            hedge_effectiveness = round(hedge_effectiveness, 4),
            effectiveness_rating = status,
            residual_risk = round(1 - hedge_effectiveness, 4)
        )