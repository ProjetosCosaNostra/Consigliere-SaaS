# Arquivo: E:\Consigliere\src\dados.py
# Função: Data Feed Enhanced (ROE & Margins)

import yfinance as yf
import pandas as pd
import numpy as np

def buscar_dados_multiticker(tickers, periodo="1y"):
    if not tickers: return pd.DataFrame()
    try:
        dados = yf.download(tickers, period=periodo, progress=False, auto_adjust=True)
        if 'Close' in dados: precos = dados['Close']
        else: precos = dados
        
        if isinstance(precos, pd.Series):
            precos = precos.to_frame()
            precos.columns = tickers
        return precos
    except: return pd.DataFrame()

def buscar_dados_detalhados(ticker, periodo="1y"):
    try:
        df = yf.download(ticker, period=periodo, interval="1d", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.droplevel(1)
        return df
    except: return pd.DataFrame()

def buscar_preco_atual_blindado(ticker):
    try:
        t = yf.Ticker(ticker)
        price = t.info.get('currentPrice') or t.info.get('regularMarketPrice')
        if price: return price
        hist = t.history(period='1d')
        if not hist.empty: return hist['Close'].iloc[-1]
        return 0.0
    except: return 0.0

def buscar_macro():
    tickers = {'Dólar': 'USDBRL=X', 'Bitcoin': 'BTC-USD', 'S&P 500': '^GSPC'}
    res = {}
    for nome, t in tickers.items():
        try:
            df = yf.download(t, period="5d", progress=False)['Close']
            if isinstance(df, pd.DataFrame): df = df.iloc[:, 0]
            if len(df) > 1:
                val = df.iloc[-1]
                var = ((val - df.iloc[-2])/df.iloc[-2])*100
                res[nome] = (val, var)
            else: res[nome] = (0, 0)
        except: res[nome] = (0, 0)
    return res

# --- ATUALIZADO: MAIS DADOS FUNDAMENTALISTAS ---
def buscar_info_fundamentalista(ticker):
    try:
        t = yf.Ticker(ticker)
        i = t.info
        raw_dy = i.get('dividendYield', 0) or 0
        
        # Novos Dados
        roe = i.get('returnOnEquity', 0) or 0
        margem = i.get('profitMargins', 0) or 0
        
        return {
            'DY': raw_dy * 100 if raw_dy < 2 else raw_dy,
            'PL': i.get('trailingPE', 0) or 0,
            'Setor': i.get('sector', 'N/A'),
            'ROE': roe * 100, # Convertendo para %
            'Margem': margem * 100 # Convertendo para %
        }
    except: return {'DY': 0, 'PL': 0, 'Setor': 'N/A', 'ROE': 0, 'Margem': 0}