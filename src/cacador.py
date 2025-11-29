# Arquivo: E:\Consigliere\src\cacador.py
# Módulo: The Hunter (Professional Setup Scanner)
# Status: V1.0 - Larry Williams & Classics

import pandas as pd
import numpy as np

def calcular_indicadores_base(df):
    """Calcula indicadores necessários para os setups."""
    df = df.copy()
    df['MME9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    
    # Bollinger
    std = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['SMA20'] + (2 * std)
    df['BB_Lower'] = df['SMA20'] - (2 * std)
    
    return df

def setup_9_1_larry_williams(df):
    """
    Setup 9.1: MME9 vira para cima (Compra) ou para baixo (Venda).
    Gatilho: Rompimento da máxima/mínima do candle que virou a média.
    """
    if len(df) < 3: return None
    
    mme9_hoje = df['MME9'].iloc[-1]
    mme9_ontem = df['MME9'].iloc[-2]
    mme9_anteontem = df['MME9'].iloc[-3]
    
    # Compra: MME9 estava caindo, agora virou para cima
    if mme9_anteontem > mme9_ontem and mme9_hoje > mme9_ontem:
        return "COMPRA (9.1 Armado)"
    
    # Venda: MME9 estava subindo, agora virou para baixo
    if mme9_anteontem < mme9_ontem and mme9_hoje < mme9_ontem:
        return "VENDA (9.1 Armado)"
        
    return None

def setup_golden_death_cross(df):
    """
    Golden Cross: SMA50 cruza acima da SMA200 (Bullish).
    Death Cross: SMA50 cruza abaixo da SMA200 (Bearish).
    """
    if len(df) < 201: return None
    
    sma50_hj = df['SMA50'].iloc[-1]; sma200_hj = df['SMA200'].iloc[-1]
    sma50_ont = df['SMA50'].iloc[-2]; sma200_ont = df['SMA200'].iloc[-2]
    
    if sma50_ont < sma200_ont and sma50_hj > sma200_hj:
        return "GOLDEN CROSS (Alta Longa)"
    if sma50_ont > sma200_ont and sma50_hj < sma200_hj:
        return "DEATH CROSS (Baixa Longa)"
        
    return None

def setup_fechou_fora_fechou_dentro(df):
    """
    Setup de Volatilidade (Bollinger):
    Preço fechou fora da banda ontem e fechou dentro hoje = Reversão.
    """
    if len(df) < 3: return None
    
    close_hj = df['Close'].iloc[-1]; upper_hj = df['BB_Upper'].iloc[-1]; lower_hj = df['BB_Lower'].iloc[-1]
    close_ont = df['Close'].iloc[-2]; upper_ont = df['BB_Upper'].iloc[-2]; lower_ont = df['BB_Lower'].iloc[-2]
    
    # Venda (Tocou em cima e voltou)
    if close_ont > upper_ont and close_hj < upper_hj:
        return "VENDA (IFFD - Reversão)"
    
    # Compra (Tocou em baixo e voltou)
    if close_ont < lower_ont and close_hj > lower_hj:
        return "COMPRA (IFFD - Reversão)"
        
    return None

def setup_inside_bar(df):
    """
    Inside Bar: Candle atual totalmente contido no anterior.
    Indica compressão e possível explosão.
    """
    if len(df) < 2: return None
    
    high_hj = df['High'].iloc[-1]; low_hj = df['Low'].iloc[-1]
    high_ont = df['High'].iloc[-2]; low_ont = df['Low'].iloc[-2]
    
    if high_hj < high_ont and low_hj > low_ont:
        return "INSIDE BAR (Aguardar Rompimento)"
        
    return None

def escanear_estrategias(df_precos):
    """
    Roda todos os setups para todos os ativos.
    """
    resultados = []
    
    for ticker in df_precos.columns:
        # Pega dados do ativo e remove NaNs
        df_ativo = df_precos[ticker].dropna()
        if df_ativo.empty: continue
        
        # Precisamos de OHLC (Open, High, Low, Close)
        # Como o df_precos original do app pode ter vindo só com 'Close' se for download em lote simples,
        # precisamos garantir que temos dados completos.
        # O app atual baixa 'Adj Close' ou 'Close'. 
        # Para setups complexos (Inside Bar), precisamos de High/Low.
        # SE o df_precos for apenas de fechamento, rodamos apenas setups de médias.
        
        # Para o MVP, assumiremos que vamos calcular apenas setups baseados em Fechamento (Médias)
        # ou faremos o download detalhado sob demanda na função principal do app.
        
        # Vamos converter a série de preços em um DataFrame genérico para calcular médias
        df_calc = pd.DataFrame({'Close': df_ativo})
        df_calc = calcular_indicadores_base(df_calc)
        
        setups_ativos = []
        
        # 1. Larry Williams 9.1
        res_91 = setup_9_1_larry_williams(df_calc)
        if res_91: setups_ativos.append(f"Larry W. {res_91}")
        
        # 2. Cruzamentos
        res_cross = setup_golden_death_cross(df_calc)
        if res_cross: setups_ativos.append(res_cross)
        
        # Se tivermos High/Low/Open no futuro, ativamos os outros.
        # Por enquanto, focamos em tendência.
        
        if setups_ativos:
            resultados.append({
                'Ativo': ticker,
                'Preço': df_ativo.iloc[-1],
                'Setups Detectados': ", ".join(setups_ativos),
                'Tendência MME9': "Alta" if df_calc['MME9'].iloc[-1] > df_calc['MME9'].iloc[-2] else "Baixa"
            })
            
    return pd.DataFrame(resultados)