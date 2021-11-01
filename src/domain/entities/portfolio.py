
import json
import yfinance as yf
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Any

class Portfolio(BaseModel):
    back_test: Optional[bool] = False

    portfolio: Optional[Any]
    history  : Optional[Any]

    def load(self):
        if self.back_test:
            with open("C:/Users/Joao/Finance/backtest/back_carteira.json", "r") as file:
                self.portfolio = json.load(file)

            
            with open("C:/Users/Joao/Finance/backtest/back_history.json", "r") as file:
                self.history = json.load(file)

        else:
            with open("C:/Users/Joao/Finance/carteira.json", "r") as file:
                self.portfolio = json.load(file)

            
            with open("C:/Users/Joao/Finance/history.json", "r") as file:
                self.history = json.load(file)
    
    def buy(self, ticker: str, date: datetime):
        
        self.portfolio[ticker] = 0
        date = date.date()

        if ticker not in self.history["COMPRA"]:
            self.history["COMPRA"][ticker] = []

        self.history["COMPRA"][ticker].append(date)

    def sell(self, ticker: str, date: datetime):

        del self.portfolio[ticker]
        date = date.date()
        
        if ticker not in self.history["VENDA"]:
            self.history["VENDA"][ticker] = []

        self.history["VENDA"][ticker].append(date)