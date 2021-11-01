# %%

import sys
sys.path.append("C:/Users/Joao/Automaton/automaton/src")

from src.services.manager.manager import Manager

manager = Manager()
manager.download_prices()
manager.analyse()

# %%

for ticker in manager.compras:
    manager.plot_ticker(ticker)
    
# %%
