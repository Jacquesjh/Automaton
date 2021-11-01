# %%

from adviser import Manager
from portfolio import Portfolio

manager   = Manager(long_average = 50, short_average = 9)
portfolio = Portfolio()

manager.download_prices()
compras, vendas = manager.get_recommendations()

# %%

watch_list = manager.watch_list

for ticker in watch_list:
    manager.plot_ticker(ticker, plot_dif = True)


# %%
