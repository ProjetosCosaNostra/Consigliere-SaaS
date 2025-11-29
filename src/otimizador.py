# Arquivo: E:\Consigliere\src\otimizador.py
# Módulo: The Architect (Markowitz Efficient Frontier)
# Status: V1.0 - Monte Carlo Optimization

import numpy as np
import pandas as pd

def simular_fronteira_eficiente(df_precos, num_portfolios=5000):
    """
    Simula milhares de combinações de pesos para encontrar a Fronteira Eficiente.
    Retorna um DataFrame com os resultados e os pesos da melhor carteira.
    """
    # 1. Preparação
    df_retornos = df_precos.pct_change().dropna()
    if df_retornos.empty: return None, None, None
    
    num_ativos = len(df_precos.columns)
    ativos = df_precos.columns.tolist()
    
    # Matrizes para armazenar resultados
    results = np.zeros((3, num_portfolios)) # [Retorno, Volatilidade, Sharpe]
    weights_record = [] # Para guardar os pesos de cada simulação
    
    # Matriz de Covariância (Risco)
    cov_matrix = df_retornos.cov()
    # Retorno Médio Anualizado
    mean_returns = df_retornos.mean() * 252 
    
    # 2. Simulação de Monte Carlo
    for i in range(num_portfolios):
        # Pesos aleatórios normalizados para somar 1 (100%)
        weights = np.random.random(num_ativos)
        weights /= np.sum(weights)
        weights_record.append(weights)
        
        # Cálculo de Retorno e Volatilidade da Carteira 'i'
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
        
        # Armazena
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std_dev
        # Sharpe Ratio (assumindo Risk Free = 0 para simplificar visualização)
        results[2,i] = results[0,i] / results[1,i]
        
    # 3. Identificar a Melhor Carteira (Max Sharpe)
    idx_max_sharpe = np.argmax(results[2])
    max_sharpe_ret = results[0, idx_max_sharpe]
    max_sharpe_vol = results[1, idx_max_sharpe]
    best_weights = dict(zip(ativos, weights_record[idx_max_sharpe]))
    
    # 4. Empacotar dados para o gráfico
    df_simulacao = pd.DataFrame({
        'Volatilidade': results[1,:],
        'Retorno': results[0,:],
        'Sharpe': results[2,:]
    })
    
    melhor_carteira = {
        'Retorno': max_sharpe_ret,
        'Volatilidade': max_sharpe_vol,
        'Pesos': best_weights
    }
    
    return df_simulacao, melhor_carteira