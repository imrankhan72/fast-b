from fastapi import FastAPI
from binance.client import Client
import pandas as pd
from config import Config

app = FastAPI()

client = Client(Config['binance']['API_KEY'], Config['binance']['API_KEY'])

info = client.get_exchange_info()

symbols = [x['symbol'] for x in info['symbols']]

exclude = ['UP', 'DOWN', 'BEAR', 'BULL']  # Exclude leverage tokens

non_lev = [symbol for symbol in symbols if all(excludes not in symbol for excludes in exclude)]

relevant = [symbol for symbol in non_lev if symbol.endswith('USDT')]

klines = {}
for symbol in relevant:
    klines[symbol] = client.get_historical_klines(symbol, '1m', '15 mins ago utc')

returns, symbols = [], []

for symbol in relevant:
    if len(klines[symbol]) > 0:
        cumret = (pd.DataFrame(klines[symbol])[4].astype(float).pct_change() + 1).prod() - 1
        returns.append(cumret)
        symbols.append(symbol)

retdf = pd.DataFrame(returns, index=symbols, columns=['ret'])
top = retdf.ret.nlargest(10)
print(top)



@app.get("/")
async def root():
    info = client.get_exchange_info()

    symbols = [x['symbol'] for x in info['symbols']]

    exclude = ['UP', 'DOWN', 'BEAR', 'BULL']  # Exclude leverage tokens

    non_lev = [symbol for symbol in symbols if all(excludes not in symbol for excludes in exclude)]

    relevant = [symbol for symbol in non_lev if symbol.endswith('USDT')]

    klines = {}
    for symbol in relevant:
        klines[symbol] = client.get_historical_klines(symbol, '1m', '15 mins ago utc')

    returns, symbols = [], []

    for symbol in relevant:
        if len(klines[symbol]) > 0:
            cumret = (pd.DataFrame(klines[symbol])[4].astype(float).pct_change() + 1).prod() - 1
            returns.append(cumret)
            symbols.append(symbol)

    retdf = pd.DataFrame(returns, index=symbols, columns=['ret'])
    top = retdf.ret.nlargest(10)
    top_table = (top.to_frame()).to_html(classes="table")
    return top

