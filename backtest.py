# %%

import numpy as np
import pandas as pd
import yfinance as yf
from adviser import Manager
from portfolio import Portfolio

asset = yf.Ticker("TAEE11.SA")

data  = asset.history(period = "3y")
dates = data.index.tolist()[-360: ]

manager   = Manager(back_test = True, back_dates = dates, long_average = 200, short_average = 50)
portfolio = Portfolio(back_test = True)
portfolio.load()

# %%

manager.download_prices(period = "4y")

# %%

manager.get_indicators()

# %%

manager.back_dates = dates

for date in manager.back_dates:
    print(f"\n\n----- {date.date()} -----")
    compras, vendas = manager.backtest(date)
    
    for compra in compras:

        if compra not in portfolio.portfolio:
            portfolio.buy(compra, date)

    for venda in vendas:

        if venda in portfolio.portfolio:
            portfolio.sell(venda, date)
            
# %%

df = pd.DataFrame.from_dict(portfolio.history).dropna()
dates = manager.back_dates

tickers = df.index.tolist()

lucro = pd.DataFrame()
lucro.index = ["lucro"]

total_in  = 0
total_out = 0
for ticker in tickers:
    asset = yf.Ticker(ticker)
    data = asset.history(period = "5y")["Close"]
    l = []
    try:
        if pd.isna(df["VENDA"].loc[ticker]):
            df["VENDA"].loc[ticker] = [dates[-1].date()]
    except:
        pass

    for i in range(len(df["VENDA"].loc[ticker])):

        start = df["COMPRA"].loc[ticker][i]
        end   = df["VENDA"].loc[ticker][i]

        dt = end - start
        total_return = (data.loc[str(end)] - data.loc[str(start)])/(data.loc[str(start)])
        daily_return = pow(1 + total_return, 1/dt.days) - 1
        l.append(total_return)

        total_in  = total_in + 1000
        total_out = total_out + (1 + total_return)*1000
    lucro[ticker] = np.mean(l)
lucro = lucro.T

# %%

import plotly.figure_factory as ff

hist = [lucro.values[:, 0]]

label = ["Lucro"]

fig = ff.create_distplot(hist, label, show_hist=False)
fig.show()
print(f"Media: {np.mean(lucro.values[:, 0])}")

print(f"Std: {np.std(lucro.values[:, 0])}")

print(f"Total que foi investido: {total_in}")
print(f"Total atual: {total_out}")
print(f"Retorno: {(total_out/total_in - 1)*100}%")

# %%
