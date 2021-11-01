
import pandas as pd
from typing import Any
from datetime import datetime

import plotly.express as px
import yfinance as yf
from pydantic import BaseModel

class MovingAverage(BaseModel):

    long_average : int = 50
    short_average: int = 14

    prices: Any
    date  : datetime
    offset: int = 5

    def calculate(self):

        date   = self.date
        prices = self.prices

        magnitude = pd.DataFrame()
        direction = pd.DataFrame()

        tickers = prices.loc[date].dropna().keys().tolist()
        
        for ticker in tickers:
            
            asset     = prices[ticker].loc[: date].dropna()
            asset_ma  = asset.rolling(self.long_average).mean()
            asset_ewm = asset.ewm(span = self.short_average, adjust = False).mean()

            df = pd.DataFrame()

            df["Price"] = asset
            df["MA"]    = asset_ma
            df["EWM"]   = asset_ewm
            df.index    = asset.index.tolist()

            dif          = pd.DataFrame(columns = ["Valor", "Direction"])
            dif["Valor"] = ((asset_ewm - asset_ma)*100/asset).dropna().values

            if dif.empty:
                pass

            else:
                dif.index = asset_ma.dropna().index.tolist()
                offset    = self.offset

                for i in range(offset, len(dif)):
                    trend = dif.iloc[i, 0] - dif.iloc[i - offset, 0]

                    if trend > 0:
                        dif.iloc[i, 1] = float(1)

                    else:
                        dif.iloc[i, 1] = float(-1)

                dif["Direction"] = (dif["Direction"].dropna()).astype(float)

                magnitude[ticker] = dif["Valor"]
                direction[ticker] = dif["Direction"]
        
        return magnitude, direction

    def plot(self, ticker: str, plot_dif: bool = False) -> None:

        prices = self.prices
        date   = self.date

        asset     = prices[ticker].loc[: date].dropna()
        asset_ma  = asset.rolling(self.long_average).mean()
        asset_ewm = asset.ewm(span = self.short_average, adjust = False).mean()

        df = pd.DataFrame()

        df["Price"] = asset
        df["MA"]    = asset_ma
        df["EWM"]   = asset_ewm

        df.index = asset.index.tolist()
        
        fig = px.line(df, title = ticker)
        fig.show()

        if plot_dif:
            dif = pd.DataFrame(columns = ["Valor", "Direction"])
            dif["Valor"] = ((asset_ewm - asset_ma)*100/asset).dropna().values

            dif.index = asset_ma.dropna().index.tolist()
            offset = self.offset

            for i in range(offset, len(dif)):
                trend = dif.iloc[i, 0] - dif.iloc[i - offset, 0]

                if trend > 0:
                    dif.iloc[i, 1] = float(1)

                else:
                    dif.iloc[i, 1] = float(-1)

            dif["Direction"] = (dif["Direction"].dropna()).astype(float)

            fig = px.line(dif, title = ticker)
            fig.show()
