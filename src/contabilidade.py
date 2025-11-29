# Arquivo: E:\Consigliere\src\contabilidade.py
# Módulo: The Accountant (Performance, Tax & Analytics)
# Status: V2.0 - Calendar Heatmap

import pandas as pd
import datetime
import calendar

def gerar_relatorio_performance(historico):
    """Gera métricas de Win Rate, Payoff e Lucro Total."""
    if not historico: return None
    
    df = pd.DataFrame(historico)
    vendas = df[df['Op'] == 'V']
    
    if vendas.empty: return None
    
    total_trades = len(vendas)
    trades_win = len(vendas[vendas['PnL'] > 0])
    
    win_rate = (trades_win / total_trades) * 100 if total_trades > 0 else 0
    
    lucro_bruto = vendas[vendas['PnL'] > 0]['PnL'].sum()
    prejuizo_bruto = abs(vendas[vendas['PnL'] < 0]['PnL'].sum())
    
    fator_lucro = (lucro_bruto / prejuizo_bruto) if prejuizo_bruto > 0 else 0
    resultado_liquido = vendas['PnL'].sum()
    
    return {
        'Total Trades': total_trades,
        'Win Rate': win_rate,
        'Profit Factor': fator_lucro,
        'Resultado Total': resultado_liquido,
        'Maior Win': vendas['PnL'].max(),
        'Maior Loss': vendas['PnL'].min()
    }

def gerar_extrato_mensal(historico):
    """Agrupa o PnL por mês/ano para lista simples."""
    if not historico: return pd.DataFrame()
    
    df = pd.DataFrame(historico)
    # Filtra vendas
    vendas = df[df['Op'] == 'V'].copy()
    
    if vendas.empty: return pd.DataFrame()
    
    # Processa Data (Assumindo formato dd/mm ou dd/mm/aaaa)
    # Vamos tentar extrair Mês e Ano corretamente
    # O formato salvo no DB é "%d/%m %H:%M" (assumindo ano atual) ou precisa ser ajustado no DB para ter ano.
    # Como o DB atual salva "dd/mm HH:MM", vamos assumir o ano atual para simplificar ou melhorar o registro no futuro.
    # Para visualização correta, vamos criar uma coluna "Mes_Ano"
    
    ano_atual = datetime.datetime.now().year
    vendas['Mes_Num'] = vendas['Data'].apply(lambda x: int(x.split('/')[1].split(' ')[0]))
    vendas['Mes_Nome'] = vendas['Mes_Num'].apply(lambda x: calendar.month_abbr[x])
    vendas['Ano'] = ano_atual # Simplificação enquanto não temos ano no DB histórico
    
    agrupado = vendas.groupby(['Ano', 'Mes_Num', 'Mes_Nome'])['PnL'].sum().reset_index()
    agrupado = agrupado.sort_values(['Ano', 'Mes_Num'])
    
    return agrupado

def gerar_matriz_heatmap(historico):
    """
    Transforma o histórico em uma matriz Pivot para o Heatmap.
    Linhas: Anos | Colunas: Meses | Valores: PnL
    """
    df_mes = gerar_extrato_mensal(historico)
    if df_mes.empty: return pd.DataFrame()
    
    # Pivotar
    matriz = df_mes.pivot(index='Ano', columns='Mes_Num', values='PnL')
    
    # Renomear colunas para nomes dos meses
    mapa_meses = {i: calendar.month_abbr[i] for i in range(1, 13)}
    matriz = matriz.rename(columns=mapa_meses)
    
    # Preencher meses vazios com 0
    matriz = matriz.fillna(0)
    
    return matriz

def estimar_darf(pnl_mes, tipo="Swing"):
    if pnl_mes <= 0: return 0.0
    aliquota = 0.20 if tipo == "Day Trade" else 0.15
    return pnl_mes * aliquota