# Arquivo: E:\Consigliere\src\bot.py
# Módulo: The Interlocutor (Chat Logic Engine)
# Status: V1.0 - Rule-Based NLP

import pandas as pd
import re
import dados as db
import cerebro as brain
import capo
import narrativa as story
import valuation as val
import macro as governor

def encontrar_ticker(texto, lista_ativos):
    """Tenta encontrar um ticker na frase do usuário."""
    texto = texto.upper()
    # 1. Busca exata na lista
    for t in lista_ativos:
        # Remove .SA para facilitar a busca (ex: PETR4 encontra PETR4.SA)
        clean_t = t.replace('.SA', '')
        if t in texto or clean_t in texto:
            return t
    
    # 2. Regex para tentar identificar padrão de ticker (ex: XXXX3, XXXX4, BTC-USD)
    match = re.search(r'\b[A-Z]{4}\d{1,2}\b', texto) # Ações BR
    if match: return match.group(0) + ".SA"
    
    match_crypto = re.search(r'\b[A-Z]{3}-USD\b', texto) # Cripto
    if match_crypto: return match_crypto.group(0)
    
    return None

def processar_pergunta(texto, lista_ativos):
    """
    Cérebro do Chatbot. Analisa a intenção e retorna a resposta.
    """
    texto_lower = texto.lower()
    ticker = encontrar_ticker(texto, lista_ativos)
    
    resposta = ""
    
    # --- INTENÇÃO 1: ANÁLISE DE ATIVO ESPECÍFICO ---
    if ticker:
        try:
            # Carrega dados mínimos para análise
            df = db.buscar_dados_detalhados(ticker, "1y")
            if df.empty: return f"⚠️ Não consegui dados recentes para {ticker}."
            
            preco_atual = df['Close'].iloc[-1]
            rsi = brain.calcular_rsi(df['Close']).iloc[-1]
            
            # Pergunta sobre VALUATION / PREÇO JUSTO
            if any(x in texto_lower for x in ['valor', 'justo', 'caro', 'barato', 'valuation', 'fundamento']):
                fund = val.obter_dados_fundamentos(ticker)
                if fund:
                    graham = val.calcular_graham(fund['lpa'], fund['vpa'])
                    score = val.diagnostico_fundamentalista(fund)
                    resposta = f"💎 **ANÁLISE DE VALOR: {ticker}**\n\n"
                    resposta += f"Preço Atual: {preco_atual:.2f}\n"
                    resposta += f"Preço Justo (Graham): {graham:.2f}\n"
                    resposta += f"Saúde Financeira: {score}/100\n"
                    resposta += f"Dividend Yield: {fund['dy']*100:.2f}%\n"
                    if graham > 0 and preco_atual < graham: resposta += "✅ **Veredito:** O ativo parece DESCONTADO."
                    else: resposta += "⚠️ **Veredito:** O ativo parece CARO ou precificado corretamente."
                else:
                    resposta = f"Não tenho dados fundamentalistas confiáveis para {ticker} (Pode ser ETF ou Cripto)."
            
            # Pergunta sobre TENDÊNCIA / GRÁFICO / ANÁLISE TÉCNICA
            elif any(x in texto_lower for x in ['grafico', 'tendencia', 'tecnica', 'subir', 'cair', 'analise', 'como esta', 'como está']):
                # Usa o gerador de narrativa
                sups, ress = brain.calcular_suporte_resistencia_auto(df)
                sup = sups[-1] if len(sups) > 0 else 0
                res = ress[-1] if len(ress) > 0 else 0
                narrativa = story.gerar_parecer_tecnico(ticker, df, rsi, sup, res)
                resposta = narrativa # Já vem formatado
                
            # Pergunta sobre COMPRA / VENDA (O Capo)
            elif any(x in texto_lower for x in ['comprar', 'vender', 'fazer', 'vale a pena', 'sinal']):
                conselho = capo.gerar_conselho_final(ticker, df.to_frame(name='Close') if 'Close' not in df.columns else df[['Close']])
                resposta = f"♟️ **CONSELHO DO CAPO: {ticker}**\n\n"
                resposta += f"**VEREDITO:** {conselho['Veredito']}\n"
                resposta += f"**Score de Convicção:** {conselho['Score']}/100\n"
                resposta += f"Detalhes: {conselho['Detalhes']}\n"
                if conselho['Score'] > 75: resposta += "\n> A oportunidade é clara. Considere aumentar posição."
                elif conselho['Score'] < 30: resposta += "\n> Risco elevado. Considere reduzir exposição."
                
            # Padrão (Preço e Variação)
            else:
                retorno = df['Close'].pct_change().iloc[-1] * 100
                resposta = f"📊 **{ticker}**\nCotação: {preco_atual:.2f}\nVariação Hoje: {retorno:+.2f}%\nRSI: {rsi:.0f}"

        except Exception as e:
            resposta = f"Erro ao analisar {ticker}: {e}"
            
    # --- INTENÇÃO 2: MACROECONOMIA ---
    elif any(x in texto_lower for x in ['mercado', 'macro', 'mundo', 'dolar', 'sp500', 'juros']):
        df_macro = governor.coletar_dados_macro()
        if not df_macro.empty:
            reg, exp, _ = governor.definir_regime_mercado(df_macro)
            resposta = f"🌍 **PANORAMA GLOBAL**\n\n"
            resposta += f"**Regime Atual:** {reg}\n"
            resposta += f"_{exp}_\n\n"
            resposta += f"🇺🇸 S&P 500: {df_macro['Equities (S&P 500)'].iloc[-1]:.0f}\n"
            resposta += f"💵 Dólar (DXY): {df_macro['Dollar (DXY)'].iloc[-1]:.2f}\n"
            resposta += f"📉 VIX (Medo): {df_macro['Volatility (VIX)'].iloc[-1]:.2f}"
        else:
            resposta = "Dados macroeconômicos indisponíveis no momento."
            
    # --- INTENÇÃO 3: AJUDA / OLÁ ---
    elif any(x in texto_lower for x in ['ola', 'oi', 'ajuda', 'help', 'bom dia', 'boa noite']):
        resposta = """👋 **Salute, Don.** Sou seu Consigliere.
        
Estou pronto para responder sobre:
1.  **Ativos:** "Analise PETR4", "Vale a pena comprar BTC-USD?", "Preço justo de VALE3".
2.  **Macro:** "Como está o mercado?", "Resumo macro".
3.  **Carteira:** (Em breve)

Basta digitar o nome do ativo e o que deseja saber."""

    # --- FALBACK ---
    else:
        resposta = "Não entendi, Padrinho. Tente mencionar um ativo (ex: PETR4) ou pergunte sobre o 'Mercado'."
        
    return resposta