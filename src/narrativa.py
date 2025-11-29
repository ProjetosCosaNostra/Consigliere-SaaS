# Arquivo: E:\Consigliere\src\narrativa.py
# Módulo: The Interpreter v1.1 (Currency Aware)

import pandas as pd
import numpy as np

def analisar_tendencia(df):
    """Determina a tendência baseada em Médias Móveis."""
    if len(df) < 50: return "Indefinida (Dados insuficientes)"
    
    preco = df['Close'].iloc[-1]
    sma20 = df['Close'].rolling(20).mean().iloc[-1]
    sma50 = df['Close'].rolling(50).mean().iloc[-1]
    
    if preco > sma20 and sma20 > sma50:
        return "ALTA Sólida 🟢"
    elif preco < sma20 and sma20 < sma50:
        return "BAIXA Forte 🔴"
    elif preco > sma20 and preco < sma50:
        return "Correção/Recuperação em Tendência de Baixa ⚠️"
    elif preco < sma20 and preco > sma50:
        return "Recuo em Tendência de Alta ⚠️"
    else:
        return "Lateralização/Indefinição ⚖️"

def analisar_volatilidade(df):
    if len(df) < 20: return "Normal"
    bb_std = df['Close'].rolling(20).std().iloc[-1]
    preco = df['Close'].iloc[-1]
    volatilidade = (bb_std / preco) * 100
    if volatilidade > 3.0: return "ALTA (Mercado Nervoso)"
    elif volatilidade < 1.0: return "BAIXA (Compressão)"
    else: return "NORMAL"

def gerar_parecer_tecnico(ticker, df, rsi, suporte, resistencia):
    """
    Escreve um relatório textual sobre o ativo com moeda dinâmica.
    """
    tendencia = analisar_tendencia(df)
    volatilidade = analisar_volatilidade(df)
    preco_atual = df['Close'].iloc[-1]
    retorno_hoje = df['Close'].pct_change().iloc[-1] * 100
    
    # --- DETECTOR DE MOEDA ---
    moeda = "R$" if ".SA" in ticker.upper() else "US$"
    
    # Construção da Narrativa
    texto = f"### 📜 Parecer Técnico: {ticker}\n\n"
    
    # 1. Contexto de Preço
    sinal_dia = "subindo" if retorno_hoje > 0 else "caindo"
    texto += f"O ativo encerrou cotado a **{moeda} {preco_atual:,.2f}**, {sinal_dia} **{abs(retorno_hoje):.2f}%** hoje. "
    texto += f"A estrutura técnica sugere uma tendência de **{tendencia}** no curto prazo.\n\n"
    
    # 2. Análise de Momento (RSI)
    texto += "**🔍 Diagnóstico de Momento:**\n"
    if rsi < 30:
        texto += f"O RSI está em {rsi:.0f} (Zona de Sobrevenda). O ativo pode estar **descontado demais**, sugerindo um possível repique técnico em breve (Mean Reversion). Fique atento a sinais de reversão.\n"
    elif rsi > 70:
        texto += f"O RSI está em {rsi:.0f} (Zona de Sobrecompra). O ativo esticou demais. O risco de uma **correção saudável** é alto. Cuidado com compras neste nível.\n"
    else:
        texto += f"O RSI em {rsi:.0f} indica uma zona neutra. O mercado aguarda um catalisador para definir a próxima pernada.\n"
        
    # 3. Volatilidade e Níveis
    texto += f"\n**🛡️ Níveis Chave:**\n"
    texto += f"A volatilidade atual está **{volatilidade}**. "
    
    dist_sup = ((preco_atual - suporte) / preco_atual) * 100
    dist_res = ((resistencia - preco_atual) / preco_atual) * 100
    
    texto += f"O suporte imediato mais relevante encontra-se em **{moeda} {suporte:,.2f}** ({dist_sup:.1f}% abaixo). "
    texto += f"A resistência (teto) está em **{moeda} {resistencia:,.2f}** ({dist_res:.1f}% acima).\n\n"
    
    # 4. Conclusão Consigliere
    texto += "**♟️ Veredito do Consigliere:**\n"
    if "ALTA" in tendencia and rsi < 60:
        texto += "> **OPORTUNIDADE:** O ativo segue em tendência de alta e não está sobrecomprado. Buscar entradas em pullbacks."
    elif "BAIXA" in tendencia and rsi > 40:
        texto += "> **CAUTELA:** A faca está caindo. Não tente adivinhar fundo (Catching a falling knife) até que haja um pivô de alta claro."
    elif rsi < 30:
        texto += "> **RISCO/RETORNO:** Agressivo. Compra contra-tendência possível devido à exaustão de venda, mas use Stop curto."
    else:
        texto += "> **NEUTRO:** Não há vantagem estatística clara (Edge) no momento. Aguardar definição."
        
    return texto