# Arquivo: E:\Consigliere\src\app.py
# Módulo: Terminal Institucional v80.0 (Final Stable Release)
# Status: Production Ready

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import os
import io
import pytz
import stripe
from dotenv import load_dotenv

# --- CARREGA AMBIENTE ---
load_dotenv()

# --- IMPORTS INTERNOS ---
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

# --- FINANCEIRO (STRIPE) ---
stripe.api_key = os.getenv("STRIPE_API_KEY")
DOMAIN_URL = "https://consigliere-saas-production.up.railway.app"
STRIPE_PRICE_ID = "price_1SYEOD8QDZ3aIwe46K3A4odA"

# --- CSS (DARK MODE ELITE) ---
st.markdown("""
<style>
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    .stApp { background-color: #000000; color: #E0E0E0; }
    h1, h2, h3 { font-family: 'Roboto', sans-serif; color: #D4AF37; }
    .stMetricValue { font-weight: bold; color: #D4AF37 !important; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #333; }
    
    /* Botões */
    div.stButton > button { font-weight: bold; border-radius: 4px; border: 1px solid #333; background-color: #151515; color: white; }
    div.stButton > button:hover { border-color: #D4AF37; color: #D4AF37; }
    
    /* Elementos Visuais */
    .paywall-card { border: 1px solid #D4AF37; background: linear-gradient(135deg, #1a1a00 0%, #000000 100%); padding: 30px; border-radius: 10px; text-align: center; margin: 20px 0; }
    .badge-open { background-color: #004d00; color: #00ff00; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; border: 1px solid #00ff00; }
    .badge-closed { background-color: #330000; color: #ff4b4b; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; border: 1px solid #ff4b4b; }
    
    /* Ticker */
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #050505; border-bottom: 1px solid #222; white-space: nowrap; padding: 8px 0; }
    .ticker-move { display: inline-block; animation: ticker 40s linear infinite; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ticker-item { display: inline-block; padding: 0 2rem; font-family: 'Consolas', monospace; font-weight: bold; color: #ccc; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES VISUAIS ---
def render_global_clock():
    utc = datetime.now(pytz.utc)
    zones = {'B3': ('America/Sao_Paulo', 10, 17), 'NYSE': ('America/New_York', 9, 16), 'LSE': ('Europe/London', 8, 16), 'TOKYO': ('Asia/Tokyo', 9, 15)}
    cols = st.columns(len(zones))
    idx = 0
    for name, (tz, o, c) in zones.items():
        loc = utc.astimezone(pytz.timezone(tz))
        stt = "<span class='badge-open'>ABERTO</span>" if o <= loc.hour < c and loc.weekday() < 5 else "<span class='badge-closed'>FECHADO</span>"
        cols[idx].markdown(f"**{name}** {loc.strftime('%H:%M')} {stt}", unsafe_allow_html=True)
        idx += 1
    st.markdown("---")

def render_ticker(df):
    if df.empty: return
    items = []
    for t, r in df.pct_change().iloc[-1].items():
        c = "#00FF00" if r >= 0 else "#FF4B4B"
        items.append(f"<span style='color:{c}'>{t} {r*100:.2f}%</span>")
    content = " | ".join(items) * 5
    st.markdown(f"<div class='ticker-wrap'><div class='ticker-move'><div class='ticker-item'>{content}</div></div></div>", unsafe_allow_html=True)

# --- FUNÇÕES FINANCEIRAS ---
def criar_checkout(uid, email):
    if not stripe.api_key: return None
    try:
        s = stripe.checkout.Session.create(
            line_items=[{'price': STRIPE_PRICE_ID, 'quantity': 1}],
            mode='subscription',
            success_url=f"{DOMAIN_URL}/?session_id={{CHECKOUT_SESSION_ID}}&uid={uid}",
            cancel_url=f"{DOMAIN_URL}/?canceled=true",
            customer_email=email,
            client_reference_id=str(uid)
        )
        return s.url
    except: return None

def verificar_pagamento(sid):
    if not stripe.api_key: return False, None
    try:
        s = stripe.checkout.Session.retrieve(sid)
        return s.payment_status == 'paid', s.client_reference_id
    except: return False, None

# --- INIT DATABASE ---
if 'db_v80' not in st.session_state:
    vault.init_db()
    # Migrações silenciosas
    try: 
        c = vault.get_connection(); cur = c.cursor()
        cur.execute("ALTER TABLE usuarios ADD COLUMN stripe_id TEXT")
        cur.execute("ALTER TABLE usuarios ADD COLUMN assinatura_status TEXT DEFAULT 'inactive'")
        c.commit(); c.close()
    except: pass
    st.session_state['db_v80'] = True

# --- HELPER FUNCTIONS ---
def checar_status_sentinela():
    try:
        if not os.path.exists("heartbeat.txt"): return False, "Offline"
        with open("heartbeat.txt", "r") as f: return (time.time() - float(f.read())) < 2400, "Online"
    except: return False, "Erro"

def ler_logs_sentinela():
    try:
        if os.path.exists("sentinela.log"):
            with open("sentinela.log", "r", encoding='utf-8') as f: return "".join(f.readlines()[-20:])
        return ""
    except: return ""

def to_excel(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as w: df.to_excel(w, index=False)
    return out.getvalue()

# ==============================================================================
# 🔐 LOGIN (GATEKEEPER)
# ==============================================================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

def check_auth():
    if st.session_state['logged_in']: return True
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("CONSIGLIERE")
        st.caption("Terminal Institucional de Inteligência")
        t1, t2 = st.tabs(["Acesso", "Registro"])
        with t1:
            u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
            if st.button("ENTRAR", use_container_width=True, type="primary"):
                res = vault.verificar_login(u, p)
                if res:
                    st.session_state.update({'logged_in':True, 'user_id':res[0], 'user_plano':res[1], 'username':u})
                    st.rerun()
                else: st.error("Acesso Negado.")
        with t2:
            nu = st.text_input("Novo Usuário"); np = st.text_input("Nova Senha", type="password")
            if st.button("CRIAR CONTA GRÁTIS", use_container_width=True):
                ok, msg = vault.criar_usuario(nu, np)
                if ok: st.success("Criado! Faça login."); time.sleep(1)
                else: st.error(msg)
        st.markdown("---")
        st.caption("⚠️ Disclaimer: Ferramenta de análise. Não é recomendação de investimento.")
    return False

if not check_auth(): st.stop()

# --- VARIÁVEIS GLOBAIS DO USUÁRIO ---
UID = st.session_state['user_id']
USER = st.session_state['username']
PLANO = st.session_state['user_plano']
IS_PRO = (PLANO in ['Soldato', 'Capo']) or (USER == 'admin')

# --- RETORNO DO PAGAMENTO ---
qp = st.query_params
if "session_id" in qp:
    ok, uid_ret = verificar_pagamento(qp["session_id"])
    if ok and str(uid_ret) == str(UID):
        c = vault.get_connection(); cur = c.cursor()
        cur.execute("UPDATE usuarios SET plano='Soldato', assinatura_status='active' WHERE id=?", (UID,))
        c.commit(); c.close()
        st.toast("Bem-vindo à Elite! Assinatura Ativa.", icon="🚀")
        st.session_state['user_plano'] = 'Soldato'
        st.query_params.clear(); time.sleep(2); st.rerun()

# --- CARGA DE DADOS ---
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = vault.carregar_portfolio(UID)
    st.session_state['historico'] = vault.carregar_historico(UID)
    st.session_state['macro_data'] = pd.DataFrame()
    st.session_state['cache_news'] = []
    st.session_state['equity_curve'] = [{'Data': datetime.now(), 'Total': 1000000}]
    st.session_state['chat_history'] = [{"role":"assistant", "content":f"Salute, {USER}. Terminal pronto."}]

# --- SIDEBAR ---
st.sidebar.title(f"👤 {USER.upper()}")
if IS_PRO: st.sidebar.success(f"PLANO: {PLANO} (VIP)")
else: st.sidebar.warning("PLANO: FREE")

opcoes = ["🏠 DASHBOARD", "💬 CHAT IA", "🧠 WAR ROOM", "🔬 DEEP DIVE", "🖥️ SCREENER", "💰 WEALTH", "📚 ACCOUNTING", "💳 ASSINATURA"]
if USER == 'admin': opcoes.append("👑 ADMIN")
page = st.sidebar.radio("MENU", opcoes)

st.sidebar.markdown("---")
status_s, _ = checar_status_sentinela()
st.sidebar.caption(f"SENTINELA: {'🟢 ON' if status_s else '🔴 OFF'}")

if st.sidebar.button("🔄 SYNC DADOS"):
    st.session_state['dados_carregados'] = True
    with st.spinner("Sincronizando..."):
        wl = vault.carregar_config('watchlist', "PETR4.SA, VALE3.SA, BTC-USD", user_id=UID)
        l = [t.strip() for t in wl.split(',')]
        st.session_state['lista_ativos'] = l
        st.session_state['df_precos'] = db.buscar_dados_multiticker(l, "1y")
        st.session_state['macro_data'] = governor.coletar_dados_macro()
        st.session_state['portfolio'] = vault.carregar_portfolio(UID)
    st.rerun()

if st.sidebar.button("🚪 SAIR"):
    st.session_state.clear(); st.rerun()

# --- PAYWALL ---
def render_paywall(nome):
    st.markdown(f"""
    <div class="paywall-card">
        <h1>🔒 {nome} BLOQUEADO</h1>
        <p>Acesso exclusivo para membros SOLDATO.</p>
        <p>Destrave o poder institucional agora.</p>
    </div>
    """, unsafe_allow_html=True)
    url = criar_checkout(UID, f"user_{UID}@email.com")
    if url: st.link_button("💳 DESTRAVAR AGORA (R$ 97,90)", url, type="primary", use_container_width=True)

# --- LÓGICA PRINCIPAL ---
if 'dados_carregados' in st.session_state and not st.session_state['df_precos'].empty:
    df = st.session_state['df_precos']; lista = st.session_state['lista_ativos']; macro = st.session_state['macro_data']
    render_ticker(df)

    if page == "🏠 DASHBOARD":
        render_global_clock()
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Panorama Macro")
            if not macro.empty:
                r, t, c = governor.definir_regime_mercado(macro)
                st.info(f"Regime: {r} | {t}")
                l = macro.iloc[-1]
                m1, m2, m3 = st.columns(3)
                m1.metric("S&P 500", f"{l['Equities (S&P 500)']:,.0f}")
                m2.metric("Dólar", f"{l['Dollar (DXY)']:.2f}")
                m3.metric("VIX", f"{l['Volatility (VIX)']:.2f}")
            st.line_chart(df)
        
        with c2:
            st.subheader("Top Picks")
            rank = capo.ranquear_oportunidades(lista, df)
            if not rank.empty: st.dataframe(rank, use_container_width=True)
        
        if IS_PRO:
            var, _ = brain.calcular_var_portfolio(st.session_state['portfolio'], df)
            st.success(f"🛡️ Risco Calculado (VaR): R$ {var:,.2f}")
        else: st.info("🔒 Risco oculto (Free).")

    elif page == "💬 CHAT IA":
        st.subheader("Consigliere AI")
        for m in st.session_state['chat_history']:
            with st.chat_message(m["role"]): st.write(m["content"])
        if p := st.chat_input("..."):
            st.session_state['chat_history'].append({"role":"user", "content":p})
            with st.chat_message("user"): st.write(p)
            with st.chat_message("assistant"):
                if IS_PRO:
                    r = bot.processar_pergunta(p, lista)
                    st.write(r); st.session_state['chat_history'].append({"role":"assistant", "content":r})
                else:
                    msg = "🔒 Chat Inteligente é exclusivo para membros."
                    st.error(msg); st.session_state['chat_history'].append({"role":"assistant", "content":msg})

    elif page == "🧠 WAR ROOM":
        if IS_PRO:
            st.subheader("War Room")
            t1, t2, t3 = st.tabs(["Risco", "Backtest", "Correlação"])
            with t1:
                vf, _ = brain.calcular_var_portfolio(st.session_state['portfolio'], df)
                st.metric("VaR 95%", f"R$ {vf:,.2f}")
            with t2:
                if st.button("Rodar RSI"):
                    res, _, ret, _ = timemachine.rodar_backtest(db.buscar_dados_detalhados(lista[0], "2y"), "RSI (Reversão)")
                    st.line_chart(res['Strategy_Equity'])
            with t3:
                st.plotly_chart(px.imshow(df.pct_change().corr(), template='plotly_dark'))
        else: render_paywall("WAR ROOM")

    elif page == "🔬 DEEP DIVE":
        st.subheader("Deep Dive")
        a = st.selectbox("Ativo", lista)
        if IS_PRO:
            d = db.buscar_dados_detalhados(a, "1y")
            p, _, s = oracle.prever_tendencia_ml(a, d)
            c1, c2 = st.columns([3,1])
            with c1: st.line_chart(d['Close'])
            with c2: st.metric("IA Prediction", s); st.progress(int(p))
        else: render_paywall("DEEP DIVE")

    elif page == "🖥️ SCREENER":
        if IS_PRO:
            st.subheader("Scanner")
            if st.button("Escanear"):
                st.dataframe(hunter.escanear_estrategias(df))
        else: render_paywall("SCREENER")

    elif page == "💰 WEALTH":
        st.subheader("Wealth Planner")
        val = st.number_input("Aporte Mensal", 1000)
        st.metric("Em 10 anos", f"R$ {val*12*10*1.1:,.2f}")

    elif page == "📚 ACCOUNTING":
        if IS_PRO:
            st.subheader("Extrato")
            st.dataframe(pd.DataFrame(st.session_state['historico']))
        else: render_paywall("ACCOUNTING")

    elif page == "💳 ASSINATURA":
        st.subheader("Sua Assinatura")
        if IS_PRO:
            st.success("Você é membro VIP. Acesso total.")
        else:
            st.info("Você está no plano Gratuito.")
            url = criar_checkout(UID, f"user_{UID}@email.com")
            if url: st.link_button("👉 ASSINAR AGORA (R$ 97,90)", url, type="primary")

    elif page == "👑 ADMIN":
        st.subheader("Admin Panel")
        c = vault.get_connection(); df_u = pd.read_sql("SELECT * FROM usuarios", c); c.close()
        st.dataframe(df_u)
        u = st.selectbox("User", df_u['username'].unique())
        if st.button("Tornar Soldato"):
            c = vault.get_connection(); cur = c.cursor()
            cur.execute("UPDATE usuarios SET plano='Soldato' WHERE username=?", (u,)); c.commit(); c.close()
            st.success("Feito!")

else: st.info("Clique em **SYNC DADOS** para iniciar.")