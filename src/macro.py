# Arquivo: E:\Consigliere\src\macro.py
# Módulo: The Governor (Global Macro Analysis)
# Status: V1.0 - Market Regimes

import yfinance as yf
import pandas as pd
import numpy as np

def coletar_dados_macro():
    """
    Coleta os principais indicadores globais.
    """
    tickers = {
        'Equities (S&P 500)': '^GSPC',
        'Rates (US 10Y)': '^TNX',
        'Dollar (DXY)': 'DX-Y.NYB',
        'Volatility (VIX)': '^VIX',
        'Energy (Oil)': 'CL=F',
        'Safe Haven (Gold)': 'GC=F'
    }
    
    try:
        # Baixa dados dos últimos 20 dias para pegar tendência curta
        df = yf.download(list(tickers.values()), period="1mo", progress=False)['Close']
        
        # Ajuste se baixar apenas 1 ativo (series) vs vários (dataframe)
        if isinstance(df, pd.Series): df = df.to_frame()
        
        # Renomear colunas para facilitar
        inv_tickers = {v: k for k, v in tickers.items()}
        df.columns = [inv_tickers.get(c, c) for c in df.columns]
        
        return df
    except Exception as e:
        print(f"Erro Macro: {e}")
        return pd.DataFrame()

def definir_regime_mercado(df_macro):
    """
    Classifica o regime de mercado baseado na correlação entre Stocks (S&P) e Rates (Juros 10Y).
    """
    if df_macro.empty: return "Dados Indisponíveis", "Neutro"
    
    # Calcula variação dos últimos 20 dias (Tendência Mensal)
    retorno_sp = df_macro['Equities (S&P 500)'].pct_change(20).iloc[-1]
    retorno_rates = df_macro['Rates (US 10Y)'].pct_change(20).iloc[-1]
    vix_atual = df_macro['Volatility (VIX)'].iloc[-1]
    dxy_atual = df_macro['Dollar (DXY)'].iloc[-1]
    
    # Lógica de Classificação de Regime
    regime = "Indefinido"
    explicacao = "Mercado sem direção clara."
    cor = "#FFFFFF"
    
    # 1. VIX Check (O Medidor de Pânico)
    if vix_atual > 30:
        return "☢️ CAPITULATION / PANIC", "Volatilidade extrema. O mercado está irracional. Cash is King.", "#FF0000"
        
    # 2. Regimes Padrão
    if retorno_sp > 0 and retorno_rates < 0:
        regime = "🐻🐻 GOLDILOCKS (Ideal)"
        explicacao = "Bolsa sobe e Juros caem. O melhor cenário para Renda Variável."
        cor = "#00FF00"
    elif retorno_sp < 0 and retorno_rates > 0:
        regime = "⚠️ INFLATION FEAR"
        explicacao = "Juros subindo estão matando a Bolsa. Risco de reprecificação global."
        cor = "#FF4B4B"
    elif retorno_sp < 0 and retorno_rates < 0:
        regime = "📉 RECESSION FEAR"
        explicacao = "Tudo cai. O mercado teme uma recessão econômica. Defensivos performam melhor."
        cor = "#FFA500" # Laranja
    elif retorno_sp > 0 and retorno_rates > 0:
        regime = "🔥 REFLATION (Ciclico)"
        explicacao = "Crescimento forte aceita juros mais altos. Bom para Commodities e Bancos."
        cor = "#00E5FF" # Cyan
        
    # Nuance do Dólar
    retorno_dxy = df_macro['Dollar (DXY)'].pct_change(20).iloc[-1]
    if retorno_dxy > 0.02:
        explicacao += " Dólar forte pressiona emergentes (Brasil)."
        
    return regime, explicacao, cor

def gerar_radar_forcas(df_macro):
    """
    Retorna valores normalizados (0-100) para um gráfico de radar das forças do mercado.
    """
    if df_macro.empty: return {}
    
    # Normalização simples baseada em Z-Score de curto prazo (20 dias)
    # Quanto maior, mais forte a tendência de alta recente
    
    ultimos = df_macro.iloc[-1]
    media = df_macro.mean()
    std = df_macro.std()
    
    z_scores = (ultimos - media) / std
    
    # Transforma Z-Score (-2 a +2) em Score (0 a 100)
    # Clip para evitar distorções extremas
    scores = {}
    for col in df_macro.columns:
        z = z_scores[col]
        score = 50 + (z * 25) 
        scores[col] = max(0, min(100, score))
        
    return scores