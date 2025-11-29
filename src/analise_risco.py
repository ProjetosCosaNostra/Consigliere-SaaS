# Arquivo: E:\Consigliere\src\analise_risco.py
# Módulo: Motor de Análise de Risco e Correlação
# Status: MVP 1.0

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from coleta_dados import buscar_historico # Importa sua ferramenta anterior

def gerar_matriz_correlacao(tickers):
    """
    Calcula e exibe a matriz de correlação entre os ativos.
    Mostra quem está "dormindo" com quem.
    """
    # 1. Puxar dados (último 1 ano é padrão)
    df = buscar_historico(tickers, periodo="1y")
    
    if df is None:
        return
    
    # 2. Limpeza de Dados (Tratando os feriados/NaN)
    # 'ffill' repete o último preço válido (se foi feriado, assume o preço de ontem)
    df_limpo = df.ffill().dropna()
    
    # 3. Cálculo dos Retornos Diários (Não olhamos preço, olhamos variação %)
    retornos = df_limpo.pct_change().dropna()
    
    # 4. A Matriz Matemática (O Segredo)
    correlacao = retornos.corr()
    
    print("\n--- MATRIZ DE CORRELAÇÃO (Números Crus) ---")
    print(correlacao.round(2)) # Mostra no terminal arredondando
    
    # 5. Gerar o Mapa de Calor Visual (O Relatório do Consigliere)
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlacao, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('CONSIGLIERE: Mapa de Risco Sistêmico')
    plt.show()

if __name__ == "__main__":
    # Carteira de Teste: 
    # Incluímos Ouro (GC=F) e Dólar (BRL=X) para ver proteções reais.
    carteira = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', '^BVSP', 'USDBRL=X', 'GC=F']
    
    print("--- Iniciando Análise de Risco ---")
    gerar_matriz_correlacao(carteira)