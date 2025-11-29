# Arquivo: E:\Consigliere\src\capo.py
# Módulo: The Capo v1.1 (Macro Aware Decision)
# Status: Production Ready

import pandas as pd
import numpy as np
import cerebro as brain
import valuation as val
import oraculo as oracle
import macro as governor # --- MELHORIA: Importando o Macro

def calcular_score_tecnico(df):
    """Avalia a tendência e momento (0-100)."""
    score = 50
    if df.empty: return 50
    preco = df['Close'].iloc[-1]
    
    # 1. Tendência
    if len(df) > 50:
        sma50 = df['Close'].rolling(50).mean().iloc[-1]
        sma200 = df['Close'].rolling(200).mean().iloc[-1] if len(df) > 200 else sma50
        if preco > sma50: score += 10
        if sma50 > sma200: score += 10 
        elif sma50 < sma200: score -= 10
    
    # 2. Momento
    rsi = brain.calcular_rsi(df['Close']).iloc[-1]
    if rsi < 30: score += 15 
    elif rsi < 45: score += 5
    elif rsi > 70: score -= 15 
    
    # 3. Volatilidade
    vwap, upper, lower = brain.calcular_vwap_bands(df)
    if preco < lower.iloc[-1]: score += 10
    elif preco > upper.iloc[-1]: score -= 10
    
    return max(0, min(100, score))

def calcular_score_fundamentalista(ticker, preco_atual):
    if ".SA" not in ticker and "USD" in ticker: return 50 
    dados = val.obter_dados_fundamentos(ticker)
    if not dados: return 50
    score = 50
    vi = val.calcular_graham(dados['lpa'], dados['vpa'])
    if vi > 0:
        upside = (vi / preco_atual) - 1
        if upside > 0.40: score += 25
        elif upside > 0.15: score += 15
        elif upside < -0.20: score -= 15
    if dados['dy'] > 0.08: score += 15
    if dados['roe'] > 0.15: score += 10
    return max(0, min(100, score))

def calcular_score_ia(ticker, df):
    prob, _, _ = oracle.prever_tendencia_ml(ticker, df)
    return prob 

def gerar_conselho_final(ticker, df_precos):
    """
    Calcula a média ponderada e aplica PENALIDADE MACRO.
    """
    if df_precos.empty: return {'Ticker': ticker, 'Score': 0, 'Veredito': "Sem Dados"}
    
    preco_atual = df_precos['Close'].iloc[-1]
    
    s_tec = calcular_score_tecnico(df_precos)
    s_fund = calcular_score_fundamentalista(ticker, preco_atual)
    s_ia = calcular_score_ia(ticker, df_precos)
    
    # Ponderação Base
    if ".SA" not in ticker: 
        score_final = (s_tec * 0.4) + (s_ia * 0.6)
    else:
        score_final = (s_tec * 0.3) + (s_fund * 0.4) + (s_ia * 0.3)

    # --- MELHORIA: AJUSTE MACROECONÔMICO (O Veto) ---
    # O Capo olha pela janela antes de autorizar.
    try:
        # Puxa dados macro rápidos (cacheado se possível, ou puxa fresh)
        # Para performance, o ideal seria passar o df_macro como argumento, 
        # mas para manter compatibilidade, vamos puxar leve.
        df_macro = governor.coletar_dados_macro()
        regime, _, _ = governor.definir_regime_mercado(df_macro)
        
        penalidade = 0
        if "PANIC" in regime or "CAPITULATION" in regime:
            penalidade = 30 # Tira 30 pontos do score em pânico
        elif "RECESSION" in regime or "INFLATION" in regime:
            penalidade = 15 # Tira 15 pontos em cenários ruins
        
        score_final = score_final - penalidade
        
    except:
        penalidade = 0 # Segue o jogo se falhar macro
        
    # Garante limites
    score_final = max(0, min(100, score_final))

    veredito = "NEUTRO"
    cor = "white"
    
    if score_final >= 80: 
        veredito = "💎 FORTE COMPRA"
        cor = "#00FF00"
    elif score_final >= 60: 
        veredito = "🟢 COMPRA"
        cor = "#90EE90"
    elif score_final <= 25: 
        veredito = "🔴 VENDA FORTE"
        cor = "#FF0000"
    elif score_final <= 40: 
        veredito = "🟠 VENDA/CAUTELA"
        cor = "#FFA500"
        
    return {
        'Ticker': ticker,
        'Preço': preco_atual,
        'Score': int(score_final),
        'Veredito': veredito,
        'Cor': cor,
        'Detalhes': f"Tec:{s_tec} | Fund:{s_fund} | IA:{int(s_ia)} | Macro Penal:-{penalidade}"
    }

def ranquear_oportunidades(lista_tickers, df_multiticker):
    ranking = []
    for t in lista_tickers:
        if t in df_multiticker.columns:
            df_ativo = df_multiticker[t].dropna().to_frame(name='Close')
            res = gerar_conselho_final(t, df_ativo)
            ranking.append(res)
    df_rank = pd.DataFrame(ranking)
    if not df_rank.empty:
        df_rank = df_rank.sort_values('Score', ascending=False)
    return df_rank