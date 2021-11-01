
import sys
sys.path.append("C:/Users/Joao/Automaton/automaton/src")

import numpy as np
import pandas as pd
from datetime import datetime

from pydantic import BaseModel

from services.manager.manager import Manager
from services.strategies.moving import MovingAverage

class Backtest(BaseModel):

    period: str = "5y"

    @classmethod
    def download_data(cls):
        
        manager = Manager()
        cls.manager = manager
        manager.download_prices(period = cls.period)

        cls.dates  = manager.prices.index.tolist()
        cls.prices = manager.prices
    
    @classmethod
    def backtest(cls, strategy: str = "Moving Averages"):

        cls.history   = {"COMPRA": dict(), "VENDA": dict()}
        cls.portfolio = []

        if strategy.lower() == "moving averages":
            strategy = MovingAverage(prices = cls.prices, date = cls.dates[-1])

            magnitude, direction = cls.manager.get_indicators(strategy)
        
        dates = magnitude.index.tolist()

        for date in dates[365: ]:
            
            compras = []
            vendas  = []
            current = magnitude.loc[date].dropna()

            for ticker in current.columns:
                data = prices[ticker].loc[: date]
                std  = np.std(data)
                mean = np.mean(data)

                atual = data.loc[date]

                if atual < (mean + 0.2*std) and atual > (mean - 2.4*std):

                    if direction[ticker].loc[date] == 1 and magnitude[ticker].loc[date] >= 0.6 and magnitude[ticker].loc[date] <= 1.4:
                        compras.append(ticker)
                    
                if direction[ticker].loc[date] == -1 and magnitude[ticker].loc[date] <= 1.5:
                    vendas.append(ticker)

            for compra in compras:

                if compra not in cls.portfolio:
                    cls.porfolio.append(compra)

                    if compra not in cls.history["COMPRA"]:
                        cls.history["COMPRA"][ticker] = []

                    cls.history["COMPRA"][ticker].append(date)

            for venda in vendas:

                if venda in cls.portfolio:
                    cls.portfolio.remove(venda)

                    if venda not in cls.history["VENDA"]:
                        cls.history["VENDA"][ticker] = []

                    cls.history["VENDA"][ticker].append(date)

    