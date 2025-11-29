# Arquivo: E:\Consigliere\src\setorial.py
# Módulo: The Maestro (Sector Rotation & Flow Analysis)
# Status: V1.0

import pandas as pd
import plotly.express as px

# Mapa Manual de Setores (Expandir conforme necessidade)
# Como APIs gratuitas falham em dar setor preciso da B3, usamos um mapa fixo robusto.
MAPA_SETORES = {
    # Commodities / Materiais Básicos
    'VALE3.SA': 'Materiais Básicos', 'CMIN3.SA': 'Materiais Básicos', 'CSNA3.SA': 'Materiais Básicos',
    'GGBR4.SA': 'Materiais Básicos', 'SUZB3.SA': 'Materiais Básicos', 'KLBN11.SA': 'Materiais Básicos',
    
    # Energia / Petróleo
    'PETR4.SA': 'Energia', 'PETR3.SA': 'Energia', 'PRIO3.SA': 'Energia', 'VBBR3.SA': 'Energia',
    'CSAN3.SA': 'Energia', 'RRRP3.SA': 'Energia',
    
    # Financeiro
    'ITUB4.SA': 'Financeiro', 'BBDC4.SA': 'Financeiro', 'BBAS3.SA': 'Financeiro',
    'SANB11.SA': 'Financeiro', 'BPAC11.SA': 'Financeiro', 'B3SA3.SA': 'Financeiro',
    
    # Utilities (Elétricas/Saneamento) - Defensivos
    'TAEE11.SA': 'Utilities', 'ELET3.SA': 'Utilities', 'CPLE6.SA': 'Utilities',
    'EQTL3.SA': 'Utilities', 'SBSP3.SA': 'Utilities', 'CMIG4.SA': 'Utilities',
    
    # Varejo / Consumo
    'MGLU3.SA': 'Consumo Cíclico', 'LREN3.SA': 'Consumo Cíclico', 'AMER3.SA': 'Consumo Cíclico',
    'JBSS3.SA': 'Consumo Não-Cíclico', 'ABEV3.SA': 'Consumo Não-Cíclico', 'RADL3.SA': 'Saúde/Varejo',
    
    # Industrial / Tech
    'WEGE3.SA': 'Industrial', 'EMBR3.SA': 'Industrial', 
    
    # Cripto / Internacional
    'BTC-USD': 'Criptoativos', 'ETH-USD': 'Criptoativos',
    'IVVB11.SA': 'Global Tech/S&P', '^GSPC': 'Global Market'
}

def identificar_setor(ticker):
    """Retorna o setor do ativo ou 'Outros' se não mapeado."""
    return MAPA_SETORES.get(ticker.strip().upper(), 'Outros')

def calcular_performance_setorial(df_precos):
    """
    Agrupa os ativos por setor e calcula a performance média.
    Retorna um DataFrame pronto para visualização.
    """
    if df_precos.empty: return pd.DataFrame()
    
    # Calcula retorno percentual do dia
    retornos = df_precos.pct_change().iloc[-1].to_frame(name='Retorno')
    retornos['Ativo'] = retornos.index
    
    # Mapeia Setores
    retornos['Setor'] = retornos['Ativo'].apply(identificar_setor)
    
    # Agrupa por Setor (Média dos ativos do setor)
    perf_setorial = retornos.groupby('Setor')['Retorno'].mean().reset_index()
    perf_setorial = perf_setorial.sort_values('Retorno', ascending=False)
    
    return perf_setorial, retornos

def gerar_arvore_setorial(df_precos):
    """
    Gera dados para o Treemap (Setor -> Ativo -> Retorno).
    """
    _, df_ativos_setor = calcular_performance_setorial(df_precos)
    
    # Adiciona uma coluna de "Valor Fictício" para tamanho do bloco se não tivermos market cap
    # Usamos valor absoluto do retorno + 1 para dar volume visual, ou fixo
    df_ativos_setor['Tamanho'] = 1 
    
    return df_ativos_setor