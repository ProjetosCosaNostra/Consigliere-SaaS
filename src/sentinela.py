# Arquivo: E:\Consigliere\src\sentinela.py
# Módulo: The Sentinel v5.0 (The Executor - Auto Trading)
# Status: V5.0 - Autonomous Execution

import time
import datetime
import dados as db
import cerebro as brain
import database as vault
import comms as voice
import cacador as hunter
import capo # O Chefe toma a decisão
import pandas as pd
import sys
import os

LOG_FILE = "sentinela.log"
HEARTBEAT_FILE = "heartbeat.txt"
INTERVALO = 1800 # 30 min

# --- REGRAS DE EXECUÇÃO ---
LOTE_PADRAO = 5000.0 # Valor financeiro por trade automático (R$)
SCORE_COMPRA = 85    # Score mínimo para comprar sozinho
SCORE_VENDA = 25     # Score máximo para vender sozinho (se tiver posição)

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [SENTINELA] {msg}")
    try: 
        with open(LOG_FILE, "a", encoding='utf-8') as f: f.write(f"[{ts}] {msg}\n")
    except: pass

def registrar_heartbeat():
    try: 
        with open(HEARTBEAT_FILE, "w") as f: f.write(str(time.time()))
    except: pass

def ciclo_vigilancia():
    registrar_heartbeat()
    
    # 1. Configurações
    token = vault.carregar_config('tg_token')
    chat_id = vault.carregar_config('tg_chat_id')
    auto_trade = vault.carregar_config('auto_trading', 'OFF') == 'ON' # Chave Mestra
    
    watchlist_str = vault.carregar_config('watchlist', 'BTC-USD')
    ativos_watch = [t.strip() for t in watchlist_str.split(',')]
    
    portfolio = vault.carregar_portfolio()
    caixa_disponivel = portfolio.get('Caixa', 0)
    ativos_port = [a for a in portfolio.keys() if a != 'Caixa']
    
    todos_ativos = list(set(ativos_watch + ativos_port))
    
    if not todos_ativos: 
        log("Lista vazia."); return

    log(f"Escaneando {len(todos_ativos)} ativos... (Auto-Trading: {auto_trade})")
    
    try:
        # Pega dados
        df_precos = db.buscar_dados_multiticker(todos_ativos, "2y") 
    except Exception as e:
        log(f"Erro dados: {e}"); return

    if df_precos.empty: return

    alertas = 0
    
    # --- A. GUARDIÃO DE POSIÇÃO (Stops & Takes) ---
    for ativo in ativos_port:
        if ativo in df_precos.columns:
            dados = portfolio[ativo]
            atual = df_precos[ativo].iloc[-1]
            stop = dados.get('stop', 0); take = dados.get('take', 0)
            
            # Stop Loss (Execução de Emergência)
            if stop > 0 and atual <= stop:
                # Se Auto-Trading ON, zera a posição
                if auto_trade:
                    qtd_venda = dados['qtd']
                    vault.registrar_trade(ativo, 'V', qtd_venda, atual, "STOP LOSS AUTOMÁTICO")
                    msg = f"🚨 **STOP EXECUTADO**: Vendi {qtd_venda}x {ativo} a {atual:.2f}"
                    log(f"EXECUÇÃO: Stop Loss em {ativo}")
                else:
                    msg = f"🚨 **STOP LOSS ACIONADO**: {ativo} em {atual:.2f} (Stop: {stop:.2f})\nRecomendação: VENDER."
                
                if token and chat_id: voice.enviar_telegram(token, chat_id, msg)
                alertas += 1
            
            # Take Profit
            if take > 0 and atual >= take:
                if auto_trade:
                    qtd_venda = dados['qtd']
                    vault.registrar_trade(ativo, 'V', qtd_venda, atual, "TAKE PROFIT AUTOMÁTICO")
                    msg = f"💰 **LUCRO NO BOLSO**: Vendi {qtd_venda}x {ativo} a {atual:.2f}"
                    log(f"EXECUÇÃO: Take Profit em {ativo}")
                else:
                    msg = f"💰 **TAKE PROFIT ATINGIDO**: {ativo} em {atual:.2f} (Alvo: {take:.2f})"
                
                if token and chat_id: voice.enviar_telegram(token, chat_id, msg)
                alertas += 1

    # --- B. OPPORTUNITY HUNTER & AUTO-TRADER ---
    for ticker in todos_ativos:
        if ticker in df_precos.columns:
            hist = df_precos[ticker].dropna()
            if len(hist) < 200: continue 
            
            # 1. Consulta o CAPO (Score Geral)
            # Precisamos criar um DF pequeno só para este ativo para passar pro Capo
            df_ativo = hist.to_frame(name='Close')
            # Adiciona volume se tiver no original (o 'cerebro' precisa para VWAP)
            # No df_precos multiticker do yfinance, as vezes vem MultiIndex. Simplificação aqui:
            # O Capo calcula indicadores internamente.
            
            decisao = capo.gerar_conselho_final(ticker, df_ativo)
            score = decisao['Score']
            preco_atual = decisao['Preço']
            
            # --- LÓGICA DE EXECUÇÃO ---
            if auto_trade:
                # COMPRA
                if score >= SCORE_COMPRA:
                    # Verifica se já tem posição (para não dobrar infinito)
                    if ticker not in ativos_port:
                        if caixa_disponivel >= LOTE_PADRAO:
                            qtd_compra = int(LOTE_PADRAO / preco_atual)
                            if qtd_compra > 0:
                                # Define Stop Técnico Automático (ATR)
                                atr = brain.calcular_atr(hist.to_frame(name='Close')).iloc[-1] # ATR simplificado
                                # Se ATR falhar (por falta de High/Low), usa 5%
                                if atr == 0: atr = preco_atual * 0.05
                                
                                stop_auto = preco_atual - (2 * atr)
                                take_auto = preco_atual + (3 * atr)
                                
                                vault.registrar_trade(ticker, 'C', qtd_compra, preco_atual, f"AUTO CAPO SCORE {score}", stop_auto, take_auto)
                                caix_disponivel = caixa_disponivel - (qtd_compra * preco_atual) # Atualiza caixa local
                                
                                msg = f"🤖 **COMPRA AUTOMÁTICA**: {ticker}\nScore: {score}/100\nQtd: {qtd_compra} @ {preco_atual:.2f}\nStop: {stop_auto:.2f}"
                                if token and chat_id: voice.enviar_telegram(token, chat_id, msg)
                                log(f"EXECUÇÃO: Compra {ticker} Score {score}")
                
                # VENDA (Saída por Score Baixo)
                elif score <= SCORE_VENDA:
                    if ticker in ativos_port:
                        qtd_pos = portfolio[ticker]['qtd']
                        if qtd_pos > 0:
                            vault.registrar_trade(ticker, 'V', qtd_pos, preco_atual, f"AUTO SAÍDA SCORE {score}")
                            msg = f"🤖 **VENDA AUTOMÁTICA**: {ticker}\nScore caiu para {score}/100\nPosição Zerada."
                            if token and chat_id: voice.enviar_telegram(token, chat_id, msg)
                            log(f"EXECUÇÃO: Venda {ticker} Score {score}")

            # --- ALERTA DE SINAL (Se não for auto trade ou apenas para log) ---
            # Se o score for muito alto, registra sinal mesmo se não comprar
            if score >= 80:
                novo = vault.registrar_sinal(ticker, f"CAPO HIGH CONVICTION ({score})", preco_atual)
                if novo and not auto_trade: # Só avisa se não comprou automático
                    msg = f"💎 **OPORTUNIDADE DE OURO**: {ticker}\nScore do Capo: {score}/100\nPreço: {preco_atual:.2f}"
                    if token and chat_id: voice.enviar_telegram(token, chat_id, msg)
                    alertas += 1

    log(f"Ciclo fim. Alertas/Execuções: {alertas}. Aguardando {INTERVALO}s...")

def iniciar_servico():
    with open(LOG_FILE, "w", encoding='utf-8') as f: f.write("--- SENTINELA v5.0 (Executor) INICIADA ---\n")
    print("--- CONSIGLIERE SENTINELA v5.0 (Executor) ---")
    vault.init_db()
    while True:
        try: ciclo_vigilancia()
        except Exception as e: log(f"ERRO FATAL: {e}")
        for i in range(INTERVALO, 0, -1):
            if i % 60 == 0: print(f"[SENTINELA] Próxima: {i//60} min...", end='\r')
            time.sleep(1)

if __name__ == "__main__":
    iniciar_servico()