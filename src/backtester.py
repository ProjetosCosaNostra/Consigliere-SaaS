# Arquivo: E:\Consigliere\src\backtester.py
# Módulo: The Time Machine (Multi-Strategy Engine)
# Status: V1.0

import pandas as pd
import numpy as np

def preparar_dados(df):
    """Calcula indicadores necessários para todas as estratégias."""
    df = df.copy()
    
    # Médias
    df['SMA9'] = df['Close'].rolling(9).mean()
    df['SMA21'] = df['Close'].rolling(21).mean()
    df['SMA50'] = df['Close'].rolling(50).mean()
    df['SMA200'] = df['Close'].rolling(200).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger (20, 2)
    std = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['SMA21'] + (2 * std)
    df['BB_Lower'] = df['SMA21'] - (2 * std)
    
    # Larry Williams 9.1 (Exponencial)
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    
    return df.dropna()

def rodar_backtest(df_raw, estrategia, capital=100000):
    """
    Simula a estratégia candle a candle.
    """
    df = preparar_dados(df_raw)
    if df.empty: return df, [], 0, 0
    
    caixa = capital
    posicao = 0
    trades = []
    equity = []
    
    preco_compra = 0
    
    # Loop Temporal
    for i in range(2, len(df)):
        # Dados Atuais e Passados
        hoje = df.iloc[i]
        ontem = df.iloc[i-1]
        anteontem = df.iloc[i-2]
        
        data = df.index[i]
        preco = hoje['Close']
        
        sinal = 0 # 0=Nada, 1=Compra, -1=Venda
        
        # --- LÓGICA DAS ESTRATÉGIAS ---
        
        if estrategia == "RSI (Reversão)":
            # Compra < 30, Vende > 70
            if hoje['RSI'] < 30: sinal = 1
            elif hoje['RSI'] > 70: sinal = -1
            
        elif estrategia == "Golden Cross (Tendência)":
            # Compra: 50 cruza acima da 200
            if ontem['SMA50'] < ontem['SMA200'] and hoje['SMA50'] > hoje['SMA200']: sinal = 1
            # Venda: 50 cruza abaixo da 200
            elif ontem['SMA50'] > ontem['SMA200'] and hoje['SMA50'] < hoje['SMA200']: sinal = -1
            
        elif estrategia == "Bollinger (Volatilidade)":
            # Compra: Fechou abaixo da banda inferior (espera retorno à média)
            if hoje['Close'] < hoje['BB_Lower']: sinal = 1
            # Venda: Tocou na banda superior
            elif hoje['Close'] > hoje['BB_Upper']: sinal = -1
            
        elif estrategia == "Larry Williams 9.1":
            # Compra: EMA9 virou para cima
            if anteontem['EMA9'] > ontem['EMA9'] and hoje['EMA9'] > ontem['EMA9']: sinal = 1
            # Venda: EMA9 virou para baixo
            elif anteontem['EMA9'] < ontem['EMA9'] and hoje['EMA9'] < ontem['EMA9']: sinal = -1

        # --- EXECUÇÃO SIMULADA ---
        
        # Compra
        if sinal == 1 and caixa > 0 and posicao == 0:
            qtd = int(caixa // preco)
            if qtd > 0:
                custo = qtd * preco
                caixa -= custo
                posicao = qtd
                preco_compra = preco
                trades.append({'Data': data, 'Tipo': 'COMPRA', 'Preço': preco, 'Qtd': qtd, 'Resultado': 0})
        
        # Venda
        elif sinal == -1 and posicao > 0:
            faturamento = posicao * preco
            lucro = faturamento - (posicao * preco_compra)
            caixa += faturamento
            trades.append({'Data': data, 'Tipo': 'VENDA', 'Preço': preco, 'Qtd': posicao, 'Resultado': lucro})
            posicao = 0
            
        # Marcação a Mercado (Equity Curve)
        valor_total = caixa + (posicao * preco)
        equity.append(valor_total)
        
    # Ajuste de tamanho do array equity para bater com o DF (removeu 2 primeiros)
    df = df.iloc[2:].copy()
    df['Strategy_Equity'] = equity
    
    # Benchmark Buy & Hold
    qtd_bh = int(capital // df['Close'].iloc[0])
    sobra = capital - (qtd_bh * df['Close'].iloc[0])
    df['BuyHold_Equity'] = (qtd_bh * df['Close']) + sobra
    
    retorno_final = ((equity[-1] - capital) / capital) * 100
    retorno_bh = ((df['BuyHold_Equity'].iloc[-1] - capital) / capital) * 100
    
    return df, trades, retorno_final, retorno_bh