# Arquivo: E:\Consigliere\src\coleta_dados.py
# Módulo: Coleta de Dados de Mercado
# Status: MVP 1.1 (Corrigido para nova API)

import yfinance as yf
import pandas as pd

def buscar_historico(tickers, periodo="1y"):
    """
    Busca dados históricos de fechamento ajustado para uma lista de ativos.
    """
    print(f"--- CONSIGLIERE: Iniciando coleta para {tickers} ---")
    
    try:
        # ATUALIZAÇÃO: auto_adjust=True garante que o preço já vem limpo (dividendos/splits)
        # A coluna agora se chama 'Close', não mais 'Adj Close'
        dados = yf.download(tickers, period=periodo, progress=False, auto_adjust=True)['Close']
        
        # Se for apenas um ativo, o pandas retorna uma Series, convertemos para DataFrame para padronizar
        if isinstance(dados, pd.Series):
            dados = dados.to_frame()
            
        print("--- Dados coletados com sucesso. ---")
        return dados

    except Exception as e:
        print(f"ERRO CRÍTICO: Falha na coleta de dados. Detalhe: {e}")
        return None

# --- ÁREA DE TESTE ---
if __name__ == "__main__":
    # Teste com alguns ativos brasileiros e americanos
    ativos_teste = ['PETR4.SA', 'VALE3.SA', '^BVSP', 'AAPL', 'BTC-USD']
    
    df = buscar_historico(ativos_teste)
    
    if df is not None:
        print("\n--- RELATÓRIO DE DADOS (Últimos 5 dias) ---")
        print(df.tail())
        print("\nO sistema está vivo e operante.")
    else:
        print("\nFalha na inicialização.")