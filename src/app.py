# Arquivo: E:\Consigliere\src\app.py
# Módulo: Terminal Institucional v84.0 (Final Database Fix)
# Status: Production Ready

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os
import io
import pytz
import stripe
from dotenv import load_dotenv

load_dotenv()

# Imports
import dados as db
import database as vault
import cerebro as brain
import capo
import bot
import macro as governor
import relatorio as scribe
import cacador as hunter
import backtester as timemachine
import contabilidade as accountant
import oraculo as oracle
import intel as spy

st.set_page_config(page_title="CONSIGLIERE", page_icon="♟️", layout="wide", initial_sidebar_state="expanded")
stripe.api_key = os.getenv("STRIPE_API_KEY")
DOMAIN_URL = "https://consigliere-saas-production.up.railway.app"
STRIPE_PRICE_ID = "price_1SYEOD8QDZ3aIwe46K3A4odA"

st.markdown("""<style>header {visibility: hidden;} .stApp {background-color: #000000; color: #E0E0E0;} section[data-testid="stSidebar"] {background-color: #0a0a0a; border-right: 1px solid #333;} div.stButton > button {font-weight: bold; border-radius: 4px; border: 1px solid #333; background-color: #151515; color: white;} div.stButton > button:hover {border-color: #D4AF37; color: #D4AF37;} .paywall-card {border: 1px solid #D4AF37; background: linear-gradient(135deg, #1a1a00 0%, #000000 100%); padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;} .ticker-wrap {width: 100%; overflow: hidden; background-color: #050505; border-bottom: 1px solid #222; white-space: nowrap; padding: 8px 0;} .ticker-move {display: inline-block; animation: ticker 40s linear infinite;} @keyframes ticker {0% {transform: translate3d(0, 0, 0);} 100% {transform: translate3d(-100%, 0, 0);}} .ticker-item {display: inline-block; padding: 0 2rem; font-family: 'Consolas', monospace; font-weight: bold; color: #ccc;}</style>""", unsafe_allow_html=True)

# --- INIT DB V3 ---
if 'db_v84' not in st.session_state:
    vault.init_db()
    st.session_state['db_v84'] = True

# --- LOGIN ---
if 'logged_in' not in st.session_state: st.session_state.update({'logged_in':False, 'user_id':None, 'username':None, 'user_plano':'Associado'})

def login_screen():
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.title("CONSIGLIERE")
        t1, t2 = st.tabs(["Login", "Registro"])
        with t1:
            u=st.text_input("User"); p=st.text_input("Pass", type="password")
            if st.button("ENTRAR"):
                r = vault.verificar_login(u, p)
                if r: st.session_state.update({'logged_in':True, 'user_id':r[0], 'user_plano':r[1], 'username':u}); st.rerun()
                else: st.error("Erro")
        with t2:
            nu=st.text_input("Novo User"); np=st.text_input("Nova Pass", type="password")
            if st.button("CRIAR"):
                ok, m = vault.criar_usuario(nu, np)
                if ok: st.success("Criado!")
                else: st.error(m)

if not st.session_state['logged_in']: login_screen(); st.stop()

# --- SISTEMA ---
UID = st.session_state['user_id']; USER = st.session_state['username']; PLANO = st.session_state['user_plano']
IS_PRO = (PLANO in ['Soldato', 'Capo']) or (USER == 'admin')

if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = vault.carregar_portfolio(UID)
    st.session_state['historico'] = vault.carregar_historico(UID)

st.sidebar.title(f"👤 {USER}")
st.sidebar.caption(f"PLANO: {PLANO}")
menu = ["🏠 DASHBOARD", "💬 CHAT", "🧠 WAR ROOM", "🔬 DEEP DIVE", "💳 ASSINATURA"]
if USER == 'admin': menu.append("👑 ADMIN")
op = st.sidebar.radio("MENU", menu)

if st.sidebar.button("🔄 SYNC"):
    with st.spinner("..."):
        l = [x.strip() for x in vault.carregar_config('watchlist', "PETR4.SA,BTC-USD", UID).split(',')]
        st.session_state['df'] = db.buscar_dados_multiticker(l, "1y")
        st.session_state['macro'] = governor.coletar_dados_macro()
    st.rerun()
if st.sidebar.button("🚪 SAIR"): st.session_state.clear(); st.rerun()

def paywall(n):
    st.markdown(f"<div class='paywall-card'><h1>🔒 {n} BLOQUEADO</h1><p>Upgrade para Soldato.</p></div>", unsafe_allow_html=True)
    if stripe.api_key:
        try:
            s = stripe.checkout.Session.create(line_items=[{'price': STRIPE_PRICE_ID, 'quantity': 1}], mode='subscription', success_url=f"{DOMAIN_URL}/?session_id={{CHECKOUT_SESSION_ID}}&uid={UID}", cancel_url=f"{DOMAIN_URL}/?canceled=true", client_reference_id=str(UID))
            st.link_button("ASSINAR", s.url)
        except: pass

# --- STRIPE CHECK ---
qp = st.query_params
if "session_id" in qp:
    if stripe.api_key:
        try:
            s = stripe.checkout.Session.retrieve(qp["session_id"])
            if s.payment_status == 'paid' and str(s.client_reference_id) == str(UID):
                conn = vault.get_connection(); c = conn.cursor()
                c.execute("UPDATE usuarios_v3 SET plano='Soldato' WHERE id=?", (UID,)); conn.commit(); conn.close()
                st.toast("Sucesso!"); st.session_state['user_plano']='Soldato'; st.query_params.clear(); time.sleep(1); st.rerun()
        except: pass

if 'df' in st.session_state:
    df = st.session_state['df']; macro = st.session_state['macro']
    
    # Ticker
    txt = " | ".join([f"{t}: {r*100:+.2f}%" for t,r in df.pct_change().iloc[-1].items()])
    st.markdown(f"<div class='ticker-wrap'><div class='ticker-move'><div class='ticker-item'>{txt}</div></div></div>", unsafe_allow_html=True)
    
    if op == "🏠 DASHBOARD":
        st.subheader("Market Overview")
        st.line_chart(df)
        if not macro.empty: st.dataframe(macro.tail(1))
        
    elif op == "💬 CHAT":
        if p:=st.chat_input(): st.write(bot.processar_pergunta(p, df.columns.tolist()))
        
    elif op == "🧠 WAR ROOM":
        if IS_PRO:
            st.subheader("War Room")
            t1, t2 = st.tabs(["Risco", "Backtest"])
            with t1: 
                var, _ = brain.calcular_var_portfolio(st.session_state['portfolio'], df)
                st.metric("VaR 95%", f"R$ {var:,.2f}")
            with t2:
                if st.button("Backtest RSI"): 
                    res, _, ret, _ = timemachine.rodar_backtest(db.buscar_dados_detalhados(df.columns[0], "2y"), "RSI (Reversão)")
                    st.line_chart(res['Strategy_Equity'])
        else: paywall("WAR ROOM")
        
    elif op == "🔬 DEEP DIVE":
        if IS_PRO:
            a = st.selectbox("Ativo", df.columns)
            d = db.buscar_dados_detalhados(a, "1y")
            st.plotly_chart(go.Figure(data=[go.Candlestick(x=d.index, open=d['Open'], close=d['Close'])]))
        else: paywall("DEEP DIVE")
        
    elif op == "💳 ASSINATURA":
        st.info(f"Plano: {PLANO}")
        if not IS_PRO: paywall("UPGRADE")
        
    elif op == "👑 ADMIN":
        conn = vault.get_connection()
        st.dataframe(pd.read_sql("SELECT * FROM usuarios_v3", conn))
        conn.close()

else: st.info("Clique em SYNC.")