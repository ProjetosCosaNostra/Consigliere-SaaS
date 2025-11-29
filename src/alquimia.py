# Arquivo: E:\Consigliere\src\alquimia.py
# Módulo: The Alchemist (Statistical Arbitrage / Pair Trading)
# Status: V1.0 - Cointegration Hunter

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint
import itertools

def calcular_zscore(series):
    """Calcula o Z-Score de uma série (desvios da média)."""
    return (series - series.mean()) / series.std()

def testar_cointegracao(series_a, series_b):
    """
    Teste de Engle-Granger para cointegração.
    Retorna: Score, P-Value e a Razão (Hedge Ratio).
    Se p_value < 0.05, os ativos têm uma 'corda invisível' que os une.
    """
    # Alinha dados
    df = pd.concat([series_a, series_b], axis=1).dropna()
    if len(df) < 30: return 0, 1.0, 0
    
    a = df.iloc[:, 0]
    b = df.iloc[:, 1]
    
    score, pvalue, _ = coint(a, b)
    
    # Calcula o Ratio (Beta do par) para saber quanto comprar de um vs vender do outro
    # Ratio = Preço A / Preço B (Simplificado) ou via OLS
    ratio = a / b
    
    return score, pvalue, ratio

def escanear_pares(df_precos, p_value_cutoff=0.05):
    """
    Testa TODOS contra TODOS na lista para achar pares.
    Isso é processamento pesado (O(n^2)), ideal para listas < 50 ativos.
    """
    ativos = df_precos.columns.tolist()
    pares_encontrados = []
    
    # Gera combinações únicas (A, B)
    combinacoes = list(itertools.combinations(ativos, 2))
    
    for a1, a2 in combinacoes:
        s1 = df_precos[a1]
        s2 = df_precos[a2]
        
        # Teste Rápido de Correlação antes do pesado (filtro)
        if s1.corr(s2) < 0.8: continue 
        
        score, pvalue, ratio_series = testar_cointegracao(s1, s2)
        
        if pvalue < p_value_cutoff:
            # Achou um par cointegrado!
            # Vamos ver se está distorcido AGORA (Oportunidade)
            zscore_atual = calcular_zscore(ratio_series).iloc[-1]
            
            pares_encontrados.append({
                'Par': f"{a1} x {a2}",
                'Ativo A': a1,
                'Ativo B': a2,
                'P-Value': pvalue,
                'Correlação': s1.corr(s2),
                'Z-Score Atual': zscore_atual,
                'Ratio Atual': ratio_series.iloc[-1],
                'Status': "Distorcido (AÇÃO)" if abs(zscore_atual) > 2.0 else "Normal"
            })
            
    return pd.DataFrame(pares_encontrados)

def analisar_par_detalhado(df_precos, ativo_a, ativo_b):
    """Gera dados para o gráfico do spread/ratio."""
    s1 = df_precos[ativo_a]
    s2 = df_precos[ativo_b]
    
    ratio = s1 / s2
    zscore = (ratio - ratio.mean()) / ratio.std()
    
    return ratio, zscore