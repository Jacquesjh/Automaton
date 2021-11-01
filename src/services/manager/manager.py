
import sys
sys.path.append("C:/Users/Joao/Automaton/automaton/src")

import pandas as pd
import numpy as np
from datetime import datetime

import yfinance as yf
from pydantic import BaseModel

from services.strategies.moving import MovingAverage

class Manager(BaseModel):

    @classmethod
    def download_prices(cls, period: str = "2y") -> None:

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
        
        print("----- Download complete! -----")
        
        cls.date   = prices.index.tolist()[-1]
        cls.prices = prices
    
    @classmethod
    def get_indicators(cls, strategy):

        cls.magnitude, cls.direction = cls.strategy.calculate()

    @classmethod
    def analyse(cls, strategy : str = "Moving Averages", date: datetime = None):
        
        if date is None:
            date = cls.date

        prices = cls.prices

        if strategy.lower() == "moving averages":

            cls.strategy = MovingAverage(prices = cls.prices, date = cls.date)
            cls.get_indicators(cls.strategy)
            
            magnitude = cls.magnitude
            direction = cls.direction

            compras    = []
            vendas     = []
            watch_list = []

            for ticker in magnitude.columns:
                
                data = prices[ticker].loc[: date]

                mean  = np.mean(data)
                std   = np.std(data)
                atual = data.loc[date]

                if atual < (mean + 0.2*std) and atual > (mean - 2.4*std):

                    if direction[ticker].loc[date] == 1 and magnitude[ticker].loc[date] >= 0.6 and magnitude[ticker].loc[date] <= 1.4:
                        compras.append(ticker)
                    
                    if direction[ticker].loc[date] == 1 and magnitude[ticker].loc[date] >= -0.3 and magnitude[ticker].loc[date] <= 2.0:
                        watch_list.append(ticker)

                if direction[ticker].loc[date] == -1 and magnitude[ticker].loc[date] <= 1.5:
                    vendas.append(ticker)

            cls.compras    = compras
            cls.vendas     = vendas
            cls.watch_list = watch_list            


    def plot_ticker(self, ticker: str, plot_dif: bool = False) -> None:

        self.strategy.plot(ticker, plot_dif)