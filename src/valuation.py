# Arquivo: E:\Consigliere\src\valuation.py
# Módulo: The Appraiser (Fundamental Valuation Engine)
# Status: V1.0 - Graham & Bazin

import yfinance as yf
import pandas as pd
import numpy as np

def obter_dados_fundamentos(ticker):
    """Busca dados específicos para valuation no Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Tratamento de erros para chaves inexistentes
        dados = {
            'preco_atual': info.get('currentPrice') or info.get('regularMarketPrice') or 0,
            'lpa': info.get('trailingEps') or 0,  # Lucro por Ação
            'vpa': info.get('bookValue') or 0,    # Valor Patrimonial por Ação
            'dy': info.get('dividendYield') or 0, # Dividend Yield (decimal)
            'roe': info.get('returnOnEquity') or 0,
            'margem_liq': info.get('profitMargins') or 0,
            'divida_liq_ebitda': 0, # Difícil pegar direto confiável sem API paga, vamos deixar zerado ou tentar estimar
            'nome': info.get('longName') or ticker
        }
        
        # Ajuste para DY se vier None
        if dados['dy'] is None: dados['dy'] = 0
        
        return dados
    except Exception as e:
        return None

def calcular_graham(lpa, vpa):
    """
    Fórmula de Benjamin Graham para Valor Intrínseco:
    VI = RaizQ(22.5 * LPA * VPA)
    """
    if lpa <= 0 or vpa <= 0:
        return 0.0 # Graham não funciona para empresas com prejuízo ou passivo a descoberto
    try:
        return np.sqrt(22.5 * lpa * vpa)
    except:
        return 0.0

def calcular_bazin(preco_atual, dy_anual_medio_esperado=0.06):
    """
    Método Décio Bazin: Preço Teto baseado em dividendos.
    Assume que o DY atual se manterá (simplificação).
    Preço Justo = Dividendos Pagos / Taxa Mínima de Atratividade (6%)
    """
    if preco_atual <= 0: return 0.0
    
    # Estimativa de dividendo em dinheiro (R$)
    # Se o sistema tiver o histórico de dividendos seria melhor, 
    # aqui usamos o Yield atual projetado sobre o preço.
    # O Yahoo manda o DY como 0.06 para 6%
    
    # Mas para calcular o teto reverso:
    # Se a empresa paga X, e eu quero 6%, quanto posso pagar?
    # X / 0.06
    
    # O DY do yahoo é (Div / Preço). Então Div = Preço * DY
    div_dinheiro = preco_atual * dy_anual_medio_esperado
    
    preco_teto = div_dinheiro / 0.06 # 6% é a taxa clássica do Bazin
    return preco_teto

def diagnostico_fundamentalista(dados):
    """Gera um score de saúde financeira (0 a 100)."""
    score = 50
    
    # Lucratividade
    if dados['roe'] > 0.15: score += 15 # ROE > 15% é excelente
    elif dados['roe'] > 0.10: score += 10
    elif dados['roe'] < 0: score -= 20 # Prejuízo
    
    if dados['margem_liq'] > 0.10: score += 10
    
    # Valuation
    vi_graham = calcular_graham(dados['lpa'], dados['vpa'])
    if vi_graham > 0:
        upside = (vi_graham / dados['preco_atual']) - 1
        if upside > 0.30: score += 15 # Desconto grande
        elif upside < -0.20: score -= 10 # Caro demais
        
    # Dividendos
    if dados['dy'] > 0.06: score += 10
    
    return min(100, max(0, score))