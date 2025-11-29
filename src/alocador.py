# Arquivo: E:\Consigliere\src\alocador.py
# Módulo: The Allocator (Manual Target Rebalancing)
# Status: V1.0

import pandas as pd

def calcular_plano_rebalanceamento(portfolio, metas, df_precos):
    """
    Compara a carteira atual com as metas (%) e gera ordens de compra/venda.
    """
    # 1. Valor Total da Carteira
    caixa = portfolio.get('Caixa', 0)
    valor_ativos = 0
    posicoes = {}
    
    # Calcula valor atual de cada posição
    for ativo, dados in portfolio.items():
        if ativo != 'Caixa':
            qtd = dados['qtd']
            # Pega preço atual se disponível, senão usa preço médio (fallback)
            preco_atual = df_precos[ativo].iloc[-1] if ativo in df_precos.columns else dados['pm']
            val = qtd * preco_atual
            valor_ativos += val
            posicoes[ativo] = {'qtd': qtd, 'valor': val, 'preco': preco_atual}
            
    total_equity = caixa + valor_ativos
    if total_equity == 0: return pd.DataFrame()
    
    # 2. Calcula Diferenças (Gap)
    plano = []
    
    # Itera sobre as metas definidas
    for ativo, target_pct in metas.items():
        target_val = total_equity * (target_pct / 100)
        
        # Dados da posição atual (ou zero se não tiver)
        pos = posicoes.get(ativo, {'qtd': 0, 'valor': 0, 'preco': 0})
        
        # Se não temos o preço no DF (ex: ativo novo na meta), tentamos buscar ou ignoramos
        if pos['preco'] == 0:
             if ativo in df_precos.columns:
                 pos['preco'] = df_precos[ativo].iloc[-1]
             else:
                 continue # Não dá pra calcular sem preço
        
        diff_valor = target_val - pos['valor']
        diff_pct = (diff_valor / total_equity) * 100
        
        # Gera Ordem
        acao = "MANTER"
        qtd_ordem = 0
        
        # Limite mínimo para agir (evita taxas em movimentos pequenos < 1%)
        if abs(diff_pct) > 1.0:
            qtd_ordem = int(diff_valor / pos['preco'])
            if qtd_ordem > 0: acao = "COMPRAR"
            elif qtd_ordem < 0: acao = "VENDER"
            
        # Só adiciona se houver ação ou para monitoramento
        plano.append({
            'Ativo': ativo,
            'Preço': pos['preco'],
            'Atual %': (pos['valor'] / total_equity) * 100,
            'Meta %': target_pct,
            'Desvio %': diff_pct,
            'Ação Sugerida': acao,
            'Qtd': abs(qtd_ordem),
            'Valor Fin.': abs(qtd_ordem * pos['preco'])
        })
        
    return pd.DataFrame(plano)