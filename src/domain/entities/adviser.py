
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime

class Manager(BaseModel):
    long_average : int = 50
    short_average: int = 14

    back_test : Optional[bool] = False
    back_dates: Optional[List[datetime]]

    date      : Optional[datetime]
    prices    : Optional[Any]
    buy_recom : Optional[List[str]]
    sell_recom: Optional[List[str]]
    indicators: Optional[Any]
    watch_list: Optional[Any]

    magnitude: Optional[Any]
    direction: Optional[Any]

    def plot_ticker(self, ticker: str, plot_dif: bool = False) -> None:
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
            offset = 3
            for i in range(offset, len(dif)):
                direction = dif.iloc[i, 0] - dif.iloc[i - offset, 0]
                if direction > 0:
                    dif.iloc[i, 1] = float(1)
                else:
                    dif.iloc[i, 1] = float(-1)
            dif["Direction"] = dif["Direction"].dropna()
            dif["Direction"] = dif["Direction"].astype(float)

            fig = px.line(dif, title = ticker)
            fig.show()

        
    def plot_recommendantions(self, plot_dif: bool = False) -> None:
        prices = self.prices
        date   = self.date

        for ticker in self.buy_recom:
            asset     = prices[ticker].loc[: date].dropna()
            asset_ma  = asset.rolling(40).mean()
            asset_ewm = asset.ewm(span = 9, adjust = False).mean()

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
                offset = 5
                for i in range(offset, len(dif)):
                    direction = dif.iloc[i, 0] - dif.iloc[i - offset, 0]
                    if direction > 0:
                        dif.iloc[i, 1] = float(1)
                    else:
                        dif.iloc[i, 1] = float(-1)

                dif["Direction"] = dif["Direction"].dropna()
                dif["Direction"] = dif["Direction"].astype(float)

                fig = px.line(dif, title = ticker)
                fig.show()

    def download_prices(self, period: str = "2y") -> None:

        ibov    = pd.read_excel("C:/Users/Joao/Finance/ibov.xlsx", header = 0)
        tickers = [ticker + ".SA" for ticker in ibov.iloc[:, 0]]
        prices  = pd.DataFrame()

        print("----- Downloading financial data -----")
        index = []

        for ticker in tickers:
            asset = yf.Ticker(ticker)
            data  = asset.history(period = period)
            prices[ticker] = data["Close"]
        
            if len(data.index.tolist()) > len(index):
                index = data.index.tolist()
        
        if not self.back_test:
            self.date = prices.index.tolist()[-1]
        
        self.prices = prices

        print("----- Download complete! -----")

    def calculate_moving_averages(self) -> None:
        prices = self.prices
        
        if self.back_test:
            date = self.back_dates[0]
            self.back_dates = self.back_dates[1: ]
        
        else:
            date = self.date

        indicators       = pd.DataFrame()
        indicators.index = ["Magnitude", "Direction"]

        tickers = prices.loc[date].dropna().keys().tolist()

        print("----- Calculating Moving Averages for each ticker -----")

        for ticker in tickers:

            asset = prices[ticker].loc[: date].dropna()
            asset_ma = asset.rolling(self.long_average).mean()
            asset_ewm = asset.ewm(span = self.short_average, adjust = False).mean()

            df = pd.DataFrame()
            df["Price"] = asset
            df["MA"] = asset_ma
            df["EWM"] = asset_ewm
            df.index = asset.index.tolist()
            dif = pd.DataFrame(columns = ["Valor", "Direction"])
            dif["Valor"] = ((asset_ewm - asset_ma)*100/asset).dropna().values

            if dif.empty:
                pass

            else:
                dif.index = asset_ma.dropna().index.tolist()
                offset = 5
                for i in range(offset, len(dif)):
                    direction = dif.iloc[i, 0] - dif.iloc[i - offset, 0]
                    if direction > 0:
                        dif.iloc[i, 1] = float(1)
                    else:
                        dif.iloc[i, 1] = float(-1)

                dif["Direction"] = dif["Direction"].dropna()
                dif["Direction"] = dif["Direction"].astype(float)

                indicators[ticker] = (dif["Valor"].loc[date], dif["Direction"].loc[date])

        self.indicators = indicators

        
    def get_indicators(self) -> None:
        
        date = self.back_dates[-1]
        self.magnitude = pd.DataFrame()
        self.direction = pd.DataFrame()
        prices = self.prices

        tickers = prices.loc[date].dropna().keys().tolist()
        magnitude = pd.DataFrame()
        direction = pd.DataFrame()

        for ticker in tickers:
            
            asset = prices[ticker].loc[: date].dropna()
            asset_ma = asset.rolling(self.long_average).mean()
            asset_ewm = asset.ewm(span = self.short_average, adjust = False).mean()

            df = pd.DataFrame()
            df["Price"] = asset
            df["MA"] = asset_ma
            df["EWM"] = asset_ewm
            df.index = asset.index.tolist()

            dif = pd.DataFrame(columns = ["Valor", "Direction"])
            dif["Valor"] = ((asset_ewm - asset_ma)*100/asset).dropna().values

            if dif.empty:
                pass

            else:
                dif.index = asset_ma.dropna().index.tolist()
                offset = 5
                for i in range(offset, len(dif)):
                    direction = dif.iloc[i, 0] - dif.iloc[i - offset, 0]
                    if direction > 0:
                        dif.iloc[i, 1] = float(1)
                    else:
                        dif.iloc[i, 1] = float(-1)

                dif["Direction"] = dif["Direction"].dropna()
                dif["Direction"] = dif["Direction"].astype(float)

                self.magnitude[ticker] = dif["Valor"]
                self.direction[ticker] = dif["Direction"]

    def backtest(self, date) -> None:
        """
        CONDIÇÕES DE COMPRA:

            DIRECTION == 1
            0.5 <= VALOR <= 1.4

        CONDIÇÕES DE VENDA:

            DIRECTION == -1
            VALOR <= 2
        """
        
        compras    = []
        vendas     = []

        magnitude = self.magnitude
        direction = self.direction
        
        for ticker in magnitude.columns:
            if direction[ticker].loc[date] == 1 and magnitude[ticker].loc[date] >= 0.8 and magnitude[ticker].loc[date] <= 1.4:
                compras.append(ticker)

            if direction[ticker].loc[date] == -1 and magnitude[ticker].loc[date] <= 1.3:
                vendas.append(ticker)

        print(f"----- Recomendações de Compra: {compras} -----")

        self.buy_recom  = compras
        self.sell_recom = vendas
        
        return compras, vendas
    
    def get_recommendations(self) -> None:

        """

        CONDIÇÕES DE COMPRA:

            DIRECTION == 1
            0.5 <= VALOR <= 1.4

        CONDIÇÕES DE VENDA:

            DIRECTION == -1
            VALOR <= 2

        """

        self.calculate_moving_averages()

        compras    = []
        vendas     = []
        watch_list = []
        indicators = self.indicators

        for ticker in indicators.columns:
            data = self.prices[ticker]

            std = np.std(data.values)
            if indicators[ticker].loc["Direction"] == 1 and indicators[ticker].loc["Magnitude"] >= 0.8 and indicators[ticker].loc["Magnitude"] <= 1.4:
                compras.append(ticker)

            if indicators[ticker].loc["Direction"] == -1 and indicators[ticker].loc["Magnitude"] <= 1.3:
                vendas.append(ticker)

            if indicators[ticker].loc["Direction"] == 1 and indicators[ticker].loc["Magnitude"] >= 0 and indicators[ticker].loc["Magnitude"] <= 2:
                watch_list.append(ticker)

        print(f"----- Recomendações de Compra: {compras} -----")

        self.buy_recom  = compras
        self.sell_recom = vendas
        self.watch_list = watch_list
        
        return compras, vendas