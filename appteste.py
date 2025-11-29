# Arquivo: E:\Consigliere\src\app.py
# Módulo: Terminal Institucional v66.2 (God Mode Edition)
# Status: Production Ready - Stable

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import time
import os
import io

# --- IMPORTS DOS MÓDULOS DO SISTEMA ---
import dados as db
import cerebro as brain
import database as vault
import intel as spy
import comms as voice
import relatorio as scribe
import narrativa as story
import oraculo as oracle
import valuation as val
import otimizador as architect
import macro as governor
import alquimia as alchemist
import contabilidade as accountant
import setorial as maestro
import cacador as hunter
import rede as network
import backtester as timemachine
import capo
import alocador as allocator
import bot

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="CONSIGLIERE | Terminal",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS (DARK MODE INSTITUCIONAL) ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #E0E0E0; }
    h1, h2, h3 { font-family: 'Roboto', sans-serif; color: #D4AF37; letter-spacing: 1px; text-transform: uppercase; }
    .stMetricValue { font-weight: bold; color: #D4AF37 !important; font-family: 'Consolas', monospace; }
    div[data-testid="stExpander"] { background-color: #111; border: 1px solid #333; }
    .stDataFrame { font-family: 'Consolas', monospace; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #333; }
    div.stButton > button { font-weight: bold; border-radius: 5px; border: 1px solid #333; background-color: #1e1e1e; color: white; transition: all 0.3s; }
    div.stButton > button:hover { border-color: #D4AF37; color: #D4AF37; }
    .risk-box { border-left: 3px solid #FF4B4B; padding-left: 10px; margin-bottom: 15px; background-color: #1a0505; }
    .status-ok { color: #00FF00; font-weight: bold; border: 1px solid #00FF00; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.8em; }
    .status-err { color: #FF4B4B; font-weight: bold; border: 1px solid #FF4B4B; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.8em; }
    .status-warn { color: #FFA500; font-weight: bold; border: 1px solid #FFA500; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.8em; }
    .narrativa-box { background-color: #0f0f0f; border-left: 4px solid #D4AF37; padding: 15px; margin-top: 10px; border-radius: 0 5px 5px 0; font-family: 'Georgia', serif; line-height: 1.6; }
    .oracle-box { background-color: #051a1a; border: 1px solid #00e5ff; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 0 10px rgba(0, 229, 255, 0.2); }
    .valuation-card { background-color: #111; border: 1px solid #333; padding: 15px; border-radius: 5px; margin-bottom: 10px; }
    .macro-card { background-color: #080808; border: 1px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    .log-box { font-family: 'Courier New', monospace; font-size: 0.7em; color: #00FF00; background-color: #000; border: 1px solid #333; padding: 10px; height: 150px; overflow-y: scroll; }
    .stChatMessage { background-color: #111; border: 1px solid #333; }
    .stChatInput { background-color: #111 !important; color: white !important; }
    a { text-decoration: none !important; }
    a:hover { text-decoration: underline !important; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def checar_status_sentinela():
    try:
        if not os.path.exists("heartbeat.txt"): return False, "Nunca Iniciada"
        with open("heartbeat.txt", "r") as f: last_beat = float(f.read())
        diff = time.time() - last_beat
        if diff < 2400: return True, f"Online ({int(diff/60)}m ago)"
        else: return False, f"Offline ({int(diff/60)}m ago)"
    except: return False, "Erro Leitura"

def ler_logs_sentinela():
    try:
        if os.path.exists("sentinela.log"):
            with open("sentinela.log", "r", encoding='utf-8') as f: linhas = f.readlines()
            return "".join(linhas[-20:])
        else: return "Arquivo de log não encontrado."
    except: return "Erro ao ler logs."

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# ==============================================================================
# 🔐 GATEKEEPER (LOGIN SYSTEM)
# ==============================================================================
if 'db_initialized' not in st.session_state:
    vault.init_db()
    st.session_state['db_initialized'] = True

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_id' not in st.session_state: st.session_state['user_id'] = None
if 'username' not in st.session_state: st.session_state['username'] = None

def check_authentication():
    if st.session_state.get('logged_in'): return True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #D4AF37;'>CONSIGLIERE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Terminal Institucional Multi-Tenant</p>", unsafe_allow_html=True)
        
        tab_in, tab_up = st.tabs(["🔑 Acessar", "📝 Registrar"])
        
        with tab_in:
            u = st.text_input("Usuário", key="login_u")
            p = st.text_input("Senha", type="password", key="login_p")
            if st.button("ENTRAR NO SISTEMA", use_container_width=True, type="primary"):
                user = vault.verificar_login(u, p)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user[0]
                    st.session_state['user_plano'] = user[1]
                    st.session_state['username'] = u
                    st.rerun()
                else: st.error("Credenciais inválidas.")
                    
        with tab_up:
            nu = st.text_input("Novo Usuário", key="reg_u")
            np = st.text_input("Nova Senha", type="password", key="reg_p")
            if st.button("CRIAR CONTA", use_container_width=True):
                ok, msg = vault.criar_usuario(nu, np)
                if ok: st.success(msg)
                else: st.error(msg)
    return False

if not check_authentication(): st.stop()
USER_ID = st.session_state['user_id']

# --- INICIALIZAÇÃO DE ESTADO (USER SPECIFIC) ---
if 'portfolio' not in st.session_state: st.session_state['portfolio'] = vault.carregar_portfolio(USER_ID)
if 'historico' not in st.session_state: st.session_state['historico'] = vault.carregar_historico(USER_ID)
if 'equity_curve' not in st.session_state: st.session_state['equity_curve'] = [{'Data': datetime.now(), 'Total': st.session_state['portfolio'].get('Caixa', 1000000)}]
if 'boleta_qtd' not in st.session_state: st.session_state['boleta_qtd'] = 100
if 'cache_news' not in st.session_state: st.session_state['cache_news'] = []
if 'last_news_update' not in st.session_state: st.session_state['last_news_update'] = datetime.now()
if 'macro_data' not in st.session_state: st.session_state['macro_data'] = pd.DataFrame()
if 'chat_history' not in st.session_state: st.session_state['chat_history'] = [{"role": "assistant", "content": f"Salute, {st.session_state['username']}. O sistema está online."}]

# Carrega Configurações do Banco de Dados (Por Usuário)
tg_token_db = vault.carregar_config('tg_token', '', user_id=USER_ID)
tg_chat_id_db = vault.carregar_config('tg_chat_id', '', user_id=USER_ID)
watchlist_db = vault.carregar_config('watchlist', "PETR4.SA, VALE3.SA, ITUB4.SA, BTC-USD", user_id=USER_ID)
auto_trading_status = vault.carregar_config('auto_trading', 'OFF', user_id=USER_ID)

# --- HEADER ---
c1, c2 = st.columns([3, 1])
with c1: st.title("CONSIGLIERE")
with c2: st.caption(f"v66.2 SaaS | User: {st.session_state['username']}")
st.markdown("---")

# --- SIDEBAR: PAINEL DE CONTROLE ---
st.sidebar.header("CONTROL PANEL")
status_sent, msg_sent = checar_status_sentinela()
if status_sent: st.sidebar.markdown(f"<div class='status-ok'>🛡️ SENTINELA: {msg_sent}</div>", unsafe_allow_html=True)
else: st.sidebar.markdown(f"<div class='status-err'>💤 SENTINELA: {msg_sent}</div>", unsafe_allow_html=True)

if auto_trading_status == 'ON': st.sidebar.markdown(f"<div class='status-ok'>🤖 AUTO-TRADING: ON</div>", unsafe_allow_html=True)
else: st.sidebar.markdown(f"<div class='status-warn'>✋ AUTO-TRADING: OFF</div>", unsafe_allow_html=True)

with st.sidebar.expander("📜 System Logs"):
    st.markdown(f"<div class='log-box'>{ler_logs_sentinela()}</div>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Botão de Pânico
with st.sidebar.expander("☢️ DANGER ZONE", expanded=False):
    st.markdown("**PROTOCOLO DE EMERGÊNCIA**")
    armado = st.checkbox("Armar Detonador")
    if armado:
        st.markdown("⚠️ **Atenção:** Isso venderá TODAS as posições a mercado.")
        if st.button("🔥 ZERAR TUDO (PANIC)", type="primary"):
            port = st.session_state['portfolio']
            log_panic = []
            for ativo, dados in port.items():
                if ativo != 'Caixa':
                    qtd = dados['qtd']
                    if qtd > 0:
                        preco = db.buscar_preco_atual_blindado(ativo)
                        vault.registrar_trade(ativo, 'V', qtd, preco, "PANIC BUTTON EXECUTION", user_id=USER_ID)
                        log_panic.append(ativo)
            if log_panic:
                if tg_token_db and tg_chat_id_db:
                    voice.enviar_telegram(tg_token_db, tg_chat_id_db, f"🚨 **PANIC BUTTON ACIONADO**\nTodas as posições de {st.session_state['username']} encerradas.")
                st.success("Ordens de ZERAGEM enviadas com sucesso.")
                st.session_state['portfolio'] = vault.carregar_portfolio(USER_ID)
                st.rerun()
            else: st.warning("Nenhuma posição aberta para zerar.")
st.sidebar.markdown("---")

# --- MENU PRINCIPAL (COM GOD MODE) ---
opcoes_menu = ["🏠 DASHBOARD", "💬 CHAT ROOM", "🖥️ MARKET SCREENER", "🔬 DEEP DIVE LAB", "🧠 WAR ROOM", "📚 ACCOUNTING", "🛑 ORDER EXECUTION"]
if st.session_state['username'] == 'admin': # Só o Don vê isso
    opcoes_menu.append("👑 GOD MODE (ADMIN)")

menu_opcao = st.sidebar.radio("MÓDULO:", options=opcoes_menu)
st.sidebar.markdown("---")

# Sidebar: Daily Movers
if 'dados_carregados' in st.session_state and not st.session_state['df_precos'].empty:
    st.sidebar.markdown("### ⚡ DAILY MOVERS")
    retornos_dia = st.session_state['df_precos'].pct_change().iloc[-1].sort_values(ascending=False)
    for t, r in retornos_dia.head(3).items(): st.sidebar.markdown(f"<span style='color:#00FF00'>🚀 {t}: +{r*100:.2f}%</span>", unsafe_allow_html=True)
    for t, r in retornos_dia.tail(3).sort_values(ascending=True).items(): st.sidebar.markdown(f"<span style='color:#FF4B4B'>🩸 {t}: {r*100:.2f}%</span>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

# Sidebar: Intel Feed
st.sidebar.markdown("### 👁️ INTEL FEED")
modo_news = st.sidebar.selectbox("Foco:", ["Geral", "Cripto", "Corporativo"])
termo_busca = "Mercado Financeiro"
if modo_news == "Cripto": termo_busca = "Bitcoin Criptomoedas"
elif modo_news == "Corporativo": termo_busca = "Resultados Empresas Bolsa B3"

if st.sidebar.button("🔄 SCAN NETWORK"):
    with st.sidebar.status("Interceptando dados..."):
        st.session_state['cache_news'] = spy.buscar_noticias_google(termo_busca, 7)
        st.session_state['last_news_update'] = datetime.now()

if st.session_state['cache_news']:
    st.sidebar.caption(f"Atualizado: {st.session_state['last_news_update'].strftime('%H:%M')}")
    for n in st.session_state['cache_news']: st.sidebar.markdown(spy.formatar_noticia_html(n), unsafe_allow_html=True)
else: st.sidebar.info("Clique em SCAN para buscar intel.")
st.sidebar.markdown("---")

# Sidebar: Configurações
st.sidebar.header("CONFIGURAÇÃO GLOBAL")
tickers_input = st.sidebar.text_area("Watchlist (Salva no DB)", value=watchlist_db, height=100)
periodo = st.sidebar.selectbox("Horizonte de Dados", ["6mo", "1y", "2y", "5y"], index=1)

with st.sidebar.expander("📲 Telegram & Sentinela"):
    tk_in = st.text_input("Bot Token", value=tg_token_db, type="password")
    id_in = st.text_input("Chat ID", value=tg_chat_id_db)
    st.markdown("### 🔑 MASTER KEY")
    auto_trade_bool = st.checkbox("Habilitar Execução Automática (Sentinela)", value=(auto_trading_status == 'ON'))
    if st.button("Salvar Configurações"):
        vault.salvar_config('tg_token', tk_in, user_id=USER_ID)
        vault.salvar_config('tg_chat_id', id_in, user_id=USER_ID)
        vault.salvar_config('watchlist', tickers_input, user_id=USER_ID)
        novo_status = 'ON' if auto_trade_bool else 'OFF'
        vault.salvar_config('auto_trading', novo_status, user_id=USER_ID)
        st.success("Configurações salvas no Cofre!")
        st.rerun()
    if st.button("Testar Conexão"):
        ok, msg = voice.enviar_telegram(tk_in, id_in, "🔔 Teste: Consigliere conectado.")
        if ok: st.sidebar.success("OK!")
        else: st.sidebar.error(msg)
    st.caption("ℹ️ Estas configurações alimentam o processo Sentinela.")

# Botão Principal de Atualização
if st.sidebar.button("ATUALIZAR SISTEMA", type="primary"):
    vault.salvar_config('watchlist', tickers_input, user_id=USER_ID)
    st.session_state['dados_carregados'] = True
    with st.spinner('Processando Dados Globais, IA e Risco...'):
        lista = [t.strip() for t in tickers_input.split(',')]
        st.session_state['lista_ativos'] = lista
        st.session_state['df_precos'] = db.buscar_dados_multiticker(lista, periodo)
        st.session_state['macro_data'] = governor.coletar_dados_macro()
        st.session_state['portfolio'] = vault.carregar_portfolio(USER_ID)
        st.session_state['historico'] = vault.carregar_historico(USER_ID)
        # =================================================================================================
#                                          NÚCLEO DO SISTEMA
# =================================================================================================

if 'dados_carregados' in st.session_state and not st.session_state['df_precos'].empty:
    df_precos = st.session_state['df_precos']
    lista = st.session_state['lista_ativos']
    df_macro = st.session_state['macro_data']

    # -------------------------------------------------------------------------------------------
    # 0. CHAT ROOM
    # -------------------------------------------------------------------------------------------
    if menu_opcao == "💬 CHAT ROOM":
        st.header("THE INTERLOCUTOR ROOM")
        st.markdown("Converse diretamente com a inteligência do Consigliere.")
        for msg in st.session_state['chat_history']:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if prompt := st.chat_input("Ex: Analise PETR4, Como está o Macro?, Vale a pena BTC?"):
            st.session_state['chat_history'].append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Consultando os arquivos..."):
                    resposta = bot.processar_pergunta(prompt, lista)
                    st.markdown(resposta)
                    st.session_state['chat_history'].append({"role": "assistant", "content": resposta})

    # -------------------------------------------------------------------------------------------
    # 1. DASHBOARD
    # -------------------------------------------------------------------------------------------
    elif menu_opcao == "🏠 DASHBOARD":
        if not df_macro.empty:
            regime, explicacao, cor_regime = governor.definir_regime_mercado(df_macro)
            st.markdown(f"""<div class='macro-card' style='border-left: 5px solid {cor_regime};'><h3 style='color: {cor_regime}; margin:0;'>🌍 GLOBAL REGIME: {regime}</h3><p style='margin:5px 0 0 0; color: #ccc;'>{explicacao}</p></div>""", unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            last_m = df_macro.iloc[-1]; ret_m = df_macro.pct_change().iloc[-1]
            m1.metric("S&P 500", f"{last_m['Equities (S&P 500)']:,.0f}", f"{ret_m['Equities (S&P 500)']*100:.2f}%")
            m2.metric("US 10Y Yield", f"{last_m['Rates (US 10Y)']:.3f}%", f"{ret_m['Rates (US 10Y)']*100:.2f}%")
            m3.metric("VIX (Fear)", f"{last_m['Volatility (VIX)']:.2f}", f"{ret_m['Volatility (VIX)']*100:.2f}%")
            m4.metric("Dólar (DXY)", f"{last_m['Dollar (DXY)']:.2f}", f"{ret_m['Dollar (DXY)']*100:.2f}%")
            st.markdown("---")

        st.subheader("⭐ CAPO'S LIST (Top Conviction)")
        with st.spinner("O Capo está deliberando..."):
            df_rank = capo.ranquear_oportunidades(lista, df_precos)
            if not df_rank.empty:
                def highlight_veredito(val): return f'color: {"#00FF00" if "COMPRA" in val else "#FF4B4B"}; font-weight: bold'
                st.dataframe(df_rank.style.applymap(highlight_veredito, subset=['Veredito']).format({'Preço': "{:.2f}", 'Score': "{:.0f}"}), use_container_width=True, height=250)
            else: st.warning("Dados insuficientes para gerar o ranking.")
        st.markdown("---")

        st.header("EXECUTIVE SUMMARY")
        port = st.session_state['portfolio']
        caixa = port.get('Caixa', 0)
        heatmap_data = []; val_ativos = 0; retornos_hoje = df_precos.pct_change().iloc[-1]
        for a, d in port.items():
            if a != 'Caixa':
                q = d['qtd']; p_atual = df_precos[a].iloc[-1] if a in df_precos else 0
                val = q * p_atual; val_ativos += val
                heatmap_data.append({'Ativo': a, 'Valor': val, 'Retorno Dia %': retornos_hoje.get(a, 0) * 100})
        total_eq = caixa + val_ativos
        sent_score = brain.calcular_sentimento_global(df_macro.to_dict() if not df_macro.empty else {})
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("NET WORTH", f"R$ {total_eq:,.2f}", delta=f" Patri: {total_eq:,.2f}")
        k2.metric("CASH", f"R$ {caixa:,.2f}")
        k3.metric("POSITIONS", f"R$ {val_ativos:,.2f}")
        k4.metric("RISK EXPOSURE", f"{val_ativos/total_eq*100:.1f}%" if total_eq > 0 else "0%")
        
        var_fin, var_pct = brain.calcular_var_portfolio(port, df_precos)
        st.markdown(f"""<div style="background-color: #1a0505; padding: 10px; border-radius: 5px; border-left: 3px solid #FF4B4B; margin-bottom: 15px;"><h4 style="margin:0; color: #FF4B4B;">🛡️ RISK SHIELD (VaR 95% - 1 Dia)</h4><p style="margin:0; color: #ccc;">Risco Máximo Estimado Hoje: <b>R$ {var_fin:,.2f}</b> ({var_pct:.2f}% do Portfolio)</p></div>""", unsafe_allow_html=True)
        
        col_report, col_vazio = st.columns([1, 5])
        with col_report:
            try:
                pdf_bytes = scribe.gerar_dossie(port, st.session_state['historico'], sent_score, df_macro.iloc[-1].to_dict() if not df_macro.empty else {}) 
                st.download_button("📄 BAIXAR DOSSIÊ", pdf_bytes, f"Dossie_{datetime.now().strftime('%Y-%m-%d')}.pdf", "application/pdf")
            except Exception as e: st.error(f"Erro PDF: {e}")
        st.markdown("---")
        
        c_radar, c_signals = st.columns([1, 1])
        with c_radar:
            st.subheader("🌍 Macro Radar Forces")
            if not df_macro.empty:
                scores_macro = governor.gerar_radar_forcas(df_macro)
                if scores_macro:
                    fig_r = go.Figure(data=go.Scatterpolar(r=list(scores_macro.values()), theta=list(scores_macro.keys()), fill='toself', line_color='#D4AF37'))
                    fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark", height=300, margin=dict(t=0, b=0, l=40, r=40))
                    st.plotly_chart(fig_r, use_container_width=True)
        with c_signals:
            st.subheader("🎯 Sniper Signals")
            sinais = []
            for t in lista:
                if t in df_precos.columns:
                    h = df_precos[t].dropna()
                    if not h.empty:
                        rsi = brain.calcular_rsi(h).iloc[-1]
                        if rsi < 25: sinais.append(f"🟢 {t}: OVERSOLD (RSI {rsi:.0f})")
                        if rsi > 75: sinais.append(f"🔴 {t}: OVERBOUGHT (RSI {rsi:.0f})")
                        if brain.detectar_baleia(h.to_frame()): sinais.append(f"🐋 {t}: WHALE ACTIVITY")
            if sinais:
                for s in sinais: st.warning(s)
            else: st.info("Sem sinais extremos no momento.")

        c_chart, c_pie = st.columns([2, 1])
        with c_chart:
            st.subheader("📈 Equity Curve")
            if len(st.session_state['equity_curve']) > 0:
                fig = px.area(pd.DataFrame(st.session_state['equity_curve']), x='Data', y='Total', color_discrete_sequence=['#D4AF37'])
                st.plotly_chart(fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=0, b=0)), use_container_width=True)
        with c_pie:
            st.subheader("Allocation")
            if heatmap_data:
                fig_map = px.treemap(pd.DataFrame(heatmap_data), path=['Ativo'], values='Valor', color='Retorno Dia %', color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
                st.plotly_chart(fig_map.update_layout(template="plotly_dark", margin=dict(t=0, b=0, l=0, r=0), height=300), use_container_width=True)

    # -------------------------------------------------------------------------------------------
    # 2. MARKET SCREENER
    # -------------------------------------------------------------------------------------------
    elif menu_opcao == "🖥️ MARKET SCREENER":
        st.header("MARKET SCREENER")
        sentimento_global = brain.calcular_sentimento_global({})
        c_gauge, c_table = st.columns([1, 3])
        with c_gauge: st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=sentimento_global, title={'text':"FEAR & GREED"}, gauge={'axis':{'range':[0,100]},'bar':{'color':"white"},'steps':[{'range':[0,25],'color':'#b71c1c'},{'range':[75,100],'color':'#1b5e20'}]})).update_layout(height=300, margin=dict(l=20,r=20,t=50,b=20), paper_bgcolor="#000", font={'color':"white"}), use_container_width=True)
        
        with c_table:
            if st.button("🔫 RUN STRATEGY SCANNER (Pro)"):
                with st.spinner("Caçando oportunidades táticas..."):
                    df_scan = hunter.escanear_estrategias(df_precos)
                    if not df_scan.empty:
                        st.success(f"Caçada concluída! {len(df_scan)} setups encontrados.")
                        st.dataframe(df_scan.style.format({'Preço': "{:.2f}"}), use_container_width=True)
                    else: st.info("Nenhum setup ativado.")
            
            st.markdown("### 📡 Live Signal Feed")
            df_sinais = vault.carregar_sinais(USER_ID)
            if not df_sinais.empty:
                df_sinais['Preço Atual'] = df_sinais['ativo'].apply(lambda x: df_precos[x].iloc[-1] if x in df_precos.columns else 0)
                df_sinais['Resultado %'] = df_sinais.apply(lambda x: ((x['Preço Atual'] - x['preco_no_sinal']) / x['preco_no_sinal']) * 100 if x['Preço Atual'] > 0 else 0, axis=1)
                def color_res(val): return 'color: #00FF00' if val > 0 else 'color: #FF4B4B'
                st.dataframe(df_sinais.style.applymap(color_res, subset=['Resultado %']).format({'preco_no_sinal': "{:.2f}", 'Preço Atual': "{:.2f}", 'Resultado %': "{:.2f}%"}), use_container_width=True)
            else: st.info("Nenhum sinal registrado.")

            st.markdown("### 📊 Screener Geral")
            infos = []
            for t in lista:
                if t in df_precos.columns:
                    hist = df_precos[t].dropna()
                    if hist.empty: continue
                    atual = hist.iloc[-1]; topo = hist.max(); dd = ((atual - topo)/topo)*100
                    rsi = brain.calcular_rsi(hist).iloc[-1]
                    fund = db.buscar_info_fundamentalista(t)
                    score = brain.calcular_score(rsi, fund['PL'], fund['DY'], dd)
                    infos.append({'Ticker': t, 'Score': score, 'Price': atual, 'RSI': rsi, 'Drawdown': dd, 'Yield': fund['DY'], 'P/E': fund['PL'], 'Setor': fund['Setor'], 'ROE': fund['ROE']})
            if infos:
                df_r = pd.DataFrame(infos)
                st.dataframe(df_r.set_index('Ticker').sort_values('Score', ascending=False).style.background_gradient(cmap='RdYlGn', subset=['Score']).format({'Price':"{:.2f}", 'Score':"{:.0f}", 'RSI':"{:.1f}", 'ROE': "{:.1f}%"}), use_container_width=True, height=300)

    # -------------------------------------------------------------------------------------------
    # 3. DEEP DIVE LAB
    # -------------------------------------------------------------------------------------------
    elif menu_opcao == "🔬 DEEP DIVE LAB":
        st.header("DEEP DIVE (INSTITUTIONAL VIEW)")
        c_sel, c_graph = st.columns([1, 3])
        with c_sel:
            ativo_foco = st.selectbox("Ativo:", lista)
            df_ohlc = db.buscar_dados_detalhados(ativo_foco, periodo)
            if not df_ohlc.empty:
                atr = brain.calcular_atr(df_ohlc).iloc[-1]; atual = df_ohlc['Close'].iloc[-1]
                stop, target, ratio = brain.calcular_setup_trade(atual, atr)
                moeda = "R$" if ".SA" in ativo_foco.upper() else "US$"
                
                st.markdown('<div class="trade-box">', unsafe_allow_html=True)
                st.subheader("🏗️ SETUP")
                st.metric("Alvo", f"{moeda} {target:,.2f}", delta=f"{(target/atual-1)*100:.1f}%")
                st.metric("Stop", f"{moeda} {stop:,.2f}", delta=f"{(stop/atual-1)*100:.1f}%", delta_color="inverse")
                st.caption(f"Risk/Reward: 1:{ratio:.1f}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                buy_press, sell_press = brain.calcular_pressao_compradora(df_ohlc)
                st.markdown("### ⚔️ Buying Pressure")
                st.progress(int(buy_press))
                
                st.markdown("---")
                st.subheader("🔮 AI PREDICTION ENGINE")
                prob, acc, sinal_ml = oracle.prever_tendencia_ml(ativo_foco, df_ohlc)
                cor_sinal = "#00FF00" if "ALTA" in sinal_ml else "#FF4B4B"
                st.markdown(f"""<div class="oracle-box" style="border-color: {cor_sinal};"><h3 style="color: {cor_sinal}; margin:0;">{sinal_ml}</h3><p style="font-size: 1.2em; margin:5px;">Probabilidade: <b>{prob:.1f}%</b></p></div>""", unsafe_allow_html=True)
                
                texto_analise = story.gerar_parecer_tecnico(ativo_foco, df_ohlc, brain.calcular_rsi(df_ohlc['Close']).iloc[-1], *brain.calcular_suporte_resistencia_auto(df_ohlc)[0:2])
                st.markdown(f'<div class="narrativa-box">{texto_analise}</div>', unsafe_allow_html=True)

        with c_graph:
            t1, t2, t3, t4 = st.tabs(["📈 Technicals", "📅 Seasonality", "⚔️ Benchmark", "💎 Valuation"])
            with t1:
                if not df_ohlc.empty:
                    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_width=[0.2, 0.2, 0.6])
                    fig.add_trace(go.Candlestick(x=df_ohlc.index, open=df_ohlc['Open'], high=df_ohlc['High'], low=df_ohlc['Low'], close=df_ohlc['Close'], name='Price'), row=1, col=1)
                    st.plotly_chart(fig.update_layout(template="plotly_dark", height=700, xaxis_rangeslider_visible=False), use_container_width=True)
            with t2:
                try:
                    piv = brain.calcular_sazonalidade(df_ohlc)
                    st.plotly_chart(px.imshow(piv, text_auto=".2f", aspect="auto", color_continuous_scale='RdYlGn').update_layout(template="plotly_dark"), use_container_width=True)
                except: st.error("Dados insuficientes.")
            with t3:
                try:
                    bench_tickers = [ativo_foco, '^GSPC']
                    df_bench_data = db.buscar_dados_multiticker(bench_tickers, periodo)
                    if not df_bench_data.empty and '^GSPC' in df_bench_data.columns:
                        st.plotly_chart(px.line((df_bench_data / df_bench_data.iloc[0]) * 100).update_layout(template="plotly_dark", height=500), use_container_width=True)
                except: pass
            with t4:
                st.subheader("💎 Fundamental Valuation Engine")
                fund = val.obter_dados_fundamentos(ativo_foco)
                if fund:
                    graham = val.calcular_graham(fund['lpa'], fund['vpa'])
                    upside = ((graham / fund['preco_atual']) - 1) * 100 if graham > 0 else 0
                    st.metric("Preço Justo (Graham)", f"{moeda} {graham:.2f}", delta=f"{upside:.1f}%")
                    st.write(fund)
                else: st.warning("Sem dados fundamentalistas.")

    # -------------------------------------------------------------------------------------------
    # 4. WAR ROOM (FULL 16 TABS)
    # -------------------------------------------------------------------------------------------
    elif menu_opcao == "🧠 WAR ROOM":
        st.header("WAR ROOM")
        # --- FIX: CÁLCULO LOCAL DE VALOR ---
        port_temp = st.session_state['portfolio']
        val_ativos = 0
        for a, d in port_temp.items():
            if a != 'Caixa' and a in df_precos.columns:
                q_temp = d['qtd'] if isinstance(d, dict) else d
                val_ativos += q_temp * df_precos[a].iloc[-1]
        # -----------------------------------
        
        t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16 = st.tabs([
            "🔙 Backtest", "🛡️ Guardian", "🔄 Rebalance", "⚖️ Allocator", "⚡ Arbitragem", 
            "⚖️ Markowitz", "📊 Risk", "💰 Monte Carlo", "🔮 AI Prophet", "🕷️ Correlation", 
            "📐 Risk Metrics", "🌪️ Stress Test", "⚗️ Alchemy (L/S)", "🛡️ Hedge Lab", "🏗️ Sector Matrix", "🕸️ The Network"
        ])
        
        pesos_ideais = brain.otimizar_portfolio(df_precos)
        capital_war = st.session_state['portfolio'].get('Caixa', 100000)
        
        # T1: Backtest
        with t1:
            st.subheader("Strategy Backtester")
            c_bt1, c_bt2 = st.columns([1, 3])
            with c_bt1:
                bt_asset = st.selectbox("Testar Ativo:", lista)
                bt_strat = st.selectbox("Estratégia", ["RSI (Reversão)", "Golden Cross (Tendência)", "Bollinger (Volatilidade)", "Larry Williams 9.1"])
                bt_cap = st.number_input("Capital Inicial", 10000, step=1000)
                if st.button("RODAR SIMULAÇÃO"):
                    with st.spinner(f"Testando {bt_strat}..."):
                        df_res, trades, ret_strat, ret_bh = timemachine.rodar_backtest(db.buscar_dados_detalhados(bt_asset, "5y"), bt_strat, bt_cap)
                        st.session_state['bt_result'] = (df_res, trades, ret_strat, ret_bh)
            with c_bt2:
                if 'bt_result' in st.session_state:
                    df_res, trades, ret_strat, ret_bh = st.session_state['bt_result']
                    m1, m2 = st.columns(2)
                    m1.metric("Retorno Estratégia", f"{ret_strat:.2f}%"); m2.metric("Retorno Buy & Hold", f"{ret_bh:.2f}%")
                    fig_bt = go.Figure()
                    fig_bt.add_trace(go.Scatter(x=df_res.index, y=df_res['Strategy_Equity'], name='Robô', line=dict(color='#00FF00')))
                    fig_bt.add_trace(go.Scatter(x=df_res.index, y=df_res['BuyHold_Equity'], name='B&H', line=dict(color='gray', dash='dot')))
                    st.plotly_chart(fig_bt.update_layout(template="plotly_dark", height=400), use_container_width=True)
                    if trades: st.dataframe(pd.DataFrame(trades), use_container_width=True)

        # T2: Guardian
        with t2:
            st.subheader("Guardian Monitor")
            mkt_proxy = df_precos.pct_change().mean(axis=1).fillna(0)
            betas = {t: brain.calcular_beta_alpha(df_precos[t].pct_change(), mkt_proxy)[0] for t in lista if t in df_precos}
            bp, al = brain.analisar_risco_portfolio(st.session_state['portfolio'], df_precos.iloc[-1], betas)
            st.metric("Portfolio Beta", f"{bp:.2f}")
            if al: 
                for a in al: st.warning(a)
            else: st.success("Sem riscos de concentração.")

        # T3: Rebalance
        with t3:
            st.subheader("Rebalanceamento Automático")
            df_ord = brain.gerar_rebalanceamento(st.session_state['portfolio'], df_precos.iloc[-1], pesos_ideais)
            if not df_ord.empty: st.dataframe(df_ord.style.format({'Preço': "R$ {:.2f}", 'Financeiro': "R$ {:.2f}"}), use_container_width=True)
            else: st.success("Balanceado.")
            # T4: Allocator
        with t4:
            st.subheader("⚖️ The Allocator: Smart Rebalancing")
            metas_atuais = vault.carregar_metas(USER_ID)
            c_aloc1, c_aloc2 = st.columns([1, 2])
            with c_aloc1:
                st.markdown("#### Definir Metas (%)")
                novas_metas = {}
                total_pct = 0
                for ativo in lista:
                    val_meta = metas_atuais.get(ativo, 0.0)
                    meta_input = st.number_input(f"{ativo} %", min_value=0.0, max_value=100.0, value=float(val_meta), key=f"m_{ativo}")
                    novas_metas[ativo] = meta_input
                    total_pct += meta_input
                st.metric("Total Alocado", f"{total_pct:.1f}%", delta_color="normal" if total_pct == 100 else "inverse")
                if st.button("SALVAR METAS"):
                    for a, p in novas_metas.items(): vault.salvar_meta(a, p, user_id=USER_ID)
                    st.success("Salvo!"); time.sleep(1); st.rerun()
            with c_aloc2:
                if metas_atuais:
                    df_plano = allocator.calcular_plano_rebalanceamento(st.session_state['portfolio'], metas_atuais, df_precos)
                    if not df_plano.empty:
                        def color_acao(val): return 'color: #00FF00; font-weight: bold' if val == 'COMPRAR' else 'color: #FF4B4B; font-weight: bold'
                        st.dataframe(df_plano.style.applymap(color_acao, subset=['Ação Sugerida']), use_container_width=True)
                        if st.button("🚀 EXECUTAR REBALANCEAMENTO"):
                            for _, row in df_plano.iterrows():
                                if row['Ação Sugerida'] in ['COMPRAR', 'VENDER']:
                                    vault.registrar_trade(row['Ativo'], 'C' if row['Ação Sugerida'] == 'COMPRAR' else 'V', row['Qtd'], row['Preço'], "AUTO REBALANCE", user_id=USER_ID)
                            st.success("Executado!"); st.session_state['portfolio'] = vault.carregar_portfolio(USER_ID); st.rerun()
                    else: st.info("Carteira balanceada.")
                else: st.warning("Defina metas.")

        # T5: Arbitrage
        with t5:
            st.subheader("Arbitrage Scanner")
            bench_arb = db.buscar_dados_detalhados('^GSPC', periodo)
            if not bench_arb.empty:
                z_scores = {t: brain.calcular_zscore_arbitragem(df_precos[t], bench_arb['Close']).iloc[-1] for t in lista if t in df_precos}
                df_z = pd.DataFrame.from_dict(z_scores, orient='index', columns=['Z-Score'])
                st.dataframe(df_z, use_container_width=True)

        # T6: Markowitz
        with t6:
            st.subheader("⚖️ Markowitz")
            if st.button("⚠️ INICIAR SIMULAÇÃO"):
                with st.spinner("Simulando..."):
                    df_sim, melhor = architect.simular_fronteira_eficiente(df_precos)
                    if df_sim is not None:
                        fig_ef = px.scatter(df_sim, x='Volatilidade', y='Retorno', color='Sharpe')
                        st.plotly_chart(fig_ef, use_container_width=True)
                        st.dataframe(pd.DataFrame.from_dict(melhor['Pesos'], orient='index', columns=['Peso']), use_container_width=True)

        # T7-T16: Other Tabs (Simplified)
        with t7: st.plotly_chart(px.histogram(df_precos.pct_change().dropna().mean(axis=1), title="Distribuição Retornos", color_discrete_sequence=['#D4AF37']).update_layout(template="plotly_dark"), use_container_width=True)
        with t8: st.plotly_chart(go.Figure([go.Scatter(y=np.mean(brain.monte_carlo_sim(df_precos, capital_war), axis=1), mode='lines', name='Expected', line=dict(color='yellow'))]).update_layout(template="plotly_dark"), use_container_width=True)
        with t9: 
            foco = st.selectbox("Ativo AI", lista, key="ai_key")
            d = db.buscar_dados_detalhados(foco, periodo)
            if not d.empty: 
                ds, pr, _ = brain.projecao_propheta(d['Close'])
                st.plotly_chart(go.Figure([go.Scatter(x=d.index, y=d['Close']), go.Scatter(x=ds, y=pr, line=dict(dash='dash'))]).update_layout(template="plotly_dark"), use_container_width=True)
        with t10: st.plotly_chart(px.imshow(brain.calcular_matriz_correlacao_raw(df_precos), text_auto=".2f", color_continuous_scale='RdYlGn_r').update_layout(template="plotly_dark"), use_container_width=True)
        with t11:
            var_fin, var_pct = brain.calcular_var_portfolio(st.session_state['portfolio'], df_precos)
            cvar_fin = brain.calcular_cvar_portfolio(st.session_state['portfolio'], df_precos)
            st.metric("VaR (95%)", f"R$ {var_fin:,.2f}"); st.metric("CVaR", f"R$ {cvar_fin:,.2f}")
        with t12:
            cenario = st.selectbox("Cenário", ["Queda S&P500 (-10%)", "Crash Bitcoin (-20%)"])
            fator = -0.10 if "S&P" in cenario else -0.20; ticker = '^GSPC' if "S&P" in cenario else 'BTC-USD'
            perda, impact = brain.executar_stress_test(st.session_state['portfolio'], df_precos, fator, ticker)
            st.metric("Impacto", f"R$ {perda:,.2f}"); st.dataframe(pd.DataFrame(impact).T)
        with t13:
            if st.button("🔍 ESCANEAR PARES"):
                df_pares = alchemist.escanear_pares(df_precos)
                if not df_pares.empty: st.dataframe(df_pares)
        with t14:
            if val_ativos > 0:
                res_hedge = brain.calcular_hedge_carteira(val_ativos, 1.0, 100, 0.2) # Simplificado
                st.write(res_hedge)
        with t15:
            perf, _ = maestro.calcular_performance_setorial(df_precos)
            if not perf.empty: st.plotly_chart(px.bar(perf, x='Retorno', y='Setor', orientation='h').update_layout(template="plotly_dark"), use_container_width=True)
        with t16:
            if st.button("🕸️ REDE"):
                fig_n = network.gerar_grafo_correlacao(df_precos)
                if fig_n: st.plotly_chart(fig_n, use_container_width=True)

    # -------------------------------------------------------------------------------------------
    # 5. ACCOUNTING
    # -------------------------------------------------------------------------------------------
    elif menu_opcao == "📚 ACCOUNTING":
        st.header("ACCOUNTING")
        hist = st.session_state['historico']
        if hist:
            report = accountant.gerar_relatorio_performance(hist)
            if report:
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Trades", f"{report['Total Trades']}"); c2.metric("Win Rate", f"{report['Win Rate']:.1f}%"); c3.metric("Resultado", f"R$ {report['Resultado Total']:,.2f}")
                st.download_button("📥 Excel", to_excel(pd.DataFrame(hist)), "Trades.xlsx")
                st.plotly_chart(px.bar(accountant.gerar_extrato_mensal(hist), x='Mes_Nome', y='PnL', title="PnL Mensal").update_layout(template="plotly_dark"), use_container_width=True)
        else: st.info("Histórico vazio.")

    # -------------------------------------------------------------------------------------------
    # 6. EXECUTION
    # -------------------------------------------------------------------------------------------
    elif menu_opcao == "🛑 ORDER EXECUTION":
        st.header("EXECUTION")
        port = st.session_state['portfolio']; caixa = port.get('Caixa', 0)
        c_boleta, c_posicao = st.columns([1, 2])
        with c_boleta:
            st.subheader("Boleta")
            ativo = st.selectbox("Ativo", lista)
            preco_mkt = db.buscar_preco_atual_blindado(ativo)
            if preco_mkt > 0:
                with st.form("boleta"):
                    qtd = st.number_input("Qtd", min_value=1, value=100)
                    stop = st.number_input("Stop Loss", value=0.0); take = st.number_input("Take Profit", value=0.0)
                    nota = st.text_input("Nota")
                    st.metric("Preço", f"R$ {preco_mkt:.2f}")
                    c_b, c_s = st.columns(2)
                    if c_b.form_submit_button("🟢 COMPRAR"):
                        if caixa >= qtd*preco_mkt:
                            vault.registrar_trade(ativo, 'C', qtd, preco_mkt, nota, stop, take, user_id=USER_ID)
                            st.session_state['portfolio'] = vault.carregar_portfolio(USER_ID)
                            st.success("Compra executada!")
                            st.rerun()
                        else: st.error("Saldo insuficiente.")
                    if c_s.form_submit_button("🔴 VENDER"):
                        if port.get(ativo, {'qtd':0})['qtd'] >= qtd:
                            vault.registrar_trade(ativo, 'V', qtd, preco_mkt, nota, user_id=USER_ID)
                            st.session_state['portfolio'] = vault.carregar_portfolio(USER_ID)
                            st.success("Venda executada!")
                            st.rerun()
                        else: st.error("Saldo insuficiente.")
            else: st.error("Mercado Fechado/Erro Cotação")

        with c_posicao:
            st.subheader("Custódia")
            pos_data = []
            for a, d in port.items():
                if a != 'Caixa': pos_data.append({"Ativo": a, "Qtd": d['qtd'], "PM": d['pm'], "Stop": d.get('stop',0)})
            if pos_data: st.dataframe(pd.DataFrame(pos_data), use_container_width=True)
            st.metric("Caixa Disponível", f"R$ {caixa:,.2f}")

    # -------------------------------------------------------------------------------------------
    # 7. GOD MODE (ADMIN PANEL)
    # -------------------------------------------------------------------------------------------
    elif menu_opcao == "👑 GOD MODE (ADMIN)":
        st.header("👑 GOD MODE: GESTÃO DA FAMÍLIA")
        st.markdown("Controle total sobre usuários e acessos do SaaS.")
        
        conn = vault.get_connection()
        df_users = pd.read_sql("SELECT id, username, plano, created_at FROM usuarios", conn)
        df_trades = pd.read_sql("SELECT * FROM trades", conn)
        conn.close()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Membros", len(df_users))
        c2.metric("Total Operações", len(df_trades))
        c3.metric("Faturamento Estimado", f"R$ {len(df_users)*99.90:,.2f}")
        st.markdown("---")
        
        c_lista, c_acoes = st.columns([2, 1])
        with c_lista:
            st.subheader("Lista de Membros")
            st.dataframe(df_users, use_container_width=True)
        with c_acoes:
            st.subheader("Operações")
            user_to_edit = st.selectbox("Selecionar Usuário", df_users['username'].unique())
            new_plan = st.selectbox("Alterar Plano", ["Associado", "Soldato", "Capo"])
            if st.button("💾 Atualizar Plano"):
                conn = vault.get_connection()
                c = conn.cursor()
                c.execute("UPDATE usuarios SET plano = ? WHERE username = ?", (new_plan, user_to_edit))
                conn.commit(); conn.close()
                st.success(f"Plano de {user_to_edit} alterado para {new_plan}!")
                time.sleep(1); st.rerun()
            st.markdown("---")
            if st.button("🗑️ BANIR USUÁRIO", type="primary"):
                if user_to_edit == 'admin': st.error("Você não pode banir o Don.")
                else:
                    conn = vault.get_connection()
                    c = conn.cursor()
                    uid = df_users[df_users['username']==user_to_edit]['id'].iloc[0]
                    c.execute("DELETE FROM usuarios WHERE id = ?", (uid,))
                    c.execute("DELETE FROM portfolio WHERE user_id = ?", (uid,))
                    c.execute("DELETE FROM trades WHERE user_id = ?", (uid,))
                    conn.commit(); conn.close()
                    st.warning(f"{user_to_edit} foi eliminado.")
                    time.sleep(1); st.rerun()

else: st.info("⚠️ Clique em 'ATUALIZAR SISTEMA' na barra lateral.")