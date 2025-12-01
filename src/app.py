# Arquivo: E:\Consigliere\src\app.py
# Módulo: Terminal Institucional v81.0 (The Hybrid Beast - Data + Sales)
# Status: Production Ready

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import os
import io
import pytz
import stripe
from dotenv import load_dotenv

# --- CARREGA AMBIENTE ---
load_dotenv()

# --- IMPORTS ---
import dados as db
import database as vault
import cerebro as brain
import intel as spy
import relatorio as scribe
import oraculo as oracle
import macro as governor
import contabilidade as accountant
import cacador as hunter
import backtester as timemachine
import capo
import bot

# --- CONFIGURAÇÃO ---
st.set_page_config(
    page_title="CONSIGLIERE | Quant Terminal",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FINANCEIRO ---
stripe.api_key = os.getenv("STRIPE_API_KEY")
DOMAIN_URL = "https://consigliere-saas-production.up.railway.app"
STRIPE_PRICE_ID = "price_1SYEOD8QDZ3aIwe46K3A4odA" 

# --- CSS DE GUERRA (VISUAL RICO) ---
st.markdown("""
<style>
    header {visibility: hidden;}
    .stApp { background-color: #050505; color: #e0e0e0; font-family: 'Roboto', sans-serif; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #000000; border-right: 1px solid #222; }
    
    /* Metrics Cards */
    .metric-container {
        background-color: #111; border: 1px solid #333; border-radius: 8px; padding: 15px; text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-val { font-size: 24px; font-weight: bold; color: #fff; }
    .metric-lbl { font-size: 12px; color: #888; text-transform: uppercase; }
    
    /* Ticker Tape */
    .ticker-wrap { width: 100%; overflow: hidden; background-color: #0a0a0a; border-bottom: 1px solid #D4AF37; white-space: nowrap; padding: 8px 0; }
    .ticker-move { display: inline-block; animation: ticker 45s linear infinite; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .ticker-item { display: inline-block; padding: 0 2rem; font-family: 'Consolas', monospace; font-weight: bold; color: #ccc; }
    
    /* Botões */
    div.stButton > button { background-color: #151515; color: #D4AF37; border: 1px solid #D4AF37; border-radius: 4px; font-weight: bold; }
    div.stButton > button:hover { background-color: #D4AF37; color: #000; }
    
    /* Paywall Blur */
    .blur { filter: blur(5px); pointer-events: none; opacity: 0.5; }
    .paywall-overlay {
        background: rgba(20, 20, 0, 0.9); border: 2px solid #D4AF37; padding: 40px; border-radius: 10px;
        text-align: center; position: relative; z-index: 999; margin-top: -200px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES VISUAIS ---
def render_ticker(df):
    if df.empty: return
    items = []
    for t, r in df.pct_change().iloc[-1].items():
        c = "#00FF00" if r >= 0 else "#FF4B4B"
        s = "▲" if r >= 0 else "▼"
        items.append(f"<span style='color:{c}'>{s} {t} {r*100:.2f}%</span>")
    content = "  |  ".join(items) * 5
    st.markdown(f"<div class='ticker-wrap'><div class='ticker-move'><div class='ticker-item'>{content}</div></div></div>", unsafe_allow_html=True)

def render_paywall(feature_name):
    url = criar_checkout(st.session_state['user_id'], f"{st.session_state['username']}@email.com")
    st.markdown(f"""
    <div class='paywall-overlay'>
        <h1>🔒 {feature_name} BLOQUEADO</h1>
        <p>Funcionalidade exclusiva para Membros SOLDATO.</p>
        <br>
        <a href="{url}" target="_blank">
            <button style="background-color:#D4AF37; color:black; font-weight:bold; padding:15px 30px; border:none; border-radius:5px; cursor:pointer;">
                DESBLOQUEAR ACESSO TOTAL (R$ 97,90)
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

# --- FUNÇÕES FINANCEIRAS ---
def criar_checkout(uid, email):
    if not stripe.api_key: return "#"
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
    except: return "#"

# --- INIT BANCO ---
if 'db_v81' not in st.session_state:
    vault.init_db()
    st.session_state['db_v81'] = True

# --- LOGIN ---
if 'logged_in' not in st.session_state: 
    st.session_state.update({'logged_in':False, 'user_id':None, 'username':None, 'user_plano':'Associado'})

def login_screen():
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<br><br><h1 style='text-align:center; color:#D4AF37;'>CONSIGLIERE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Terminal Quantitativo Institucional</p>", unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["🔑 Acessar", "📝 Nova Conta"])
        with t1:
            u = st.text_input("Usuário", key="l_u")
            p = st.text_input("Senha", type="password", key="l_p")
            if st.button("ENTRAR NO TERMINAL", use_container_width=True, type="primary"):
                res = vault.verificar_login(u, p)
                if res:
                    st.session_state.update({'logged_in':True, 'user_id':res[0], 'user_plano':res[1], 'username':u})
                    st.rerun()
                else: st.error("Usuário ou senha incorretos.")
        with t2:
            nu = st.text_input("Novo Usuário", key="r_u")
            np = st.text_input("Nova Senha", type="password", key="r_p")
            if st.button("CRIAR CONTA", use_container_width=True):
                ok, msg = vault.criar_usuario(nu, np)
                if ok: st.success("Conta criada! Faça login na aba ao lado.")
                else: st.error(msg)

if not st.session_state['logged_in']:
    login_screen()
    st.stop()

# --- SISTEMA LOGADO ---
UID = st.session_state['user_id']
USER = st.session_state['username']
PLANO = st.session_state['user_plano']
IS_PRO = (PLANO in ['Soldato', 'Capo']) or (USER == 'admin')

# Sync Data
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = vault.carregar_portfolio(UID)
    st.session_state['historico'] = vault.carregar_historico(UID)
    
# Sidebar
st.sidebar.markdown(f"### 👤 {USER.upper()}")
if IS_PRO: st.sidebar.success(f"PLANO: {PLANO}")
else: st.sidebar.warning("PLANO: FREE (Limitado)")
st.sidebar.markdown("---")

menu = ["🏠 DASHBOARD", "🧪 CRYPTO LAB", "🧠 WAR ROOM", "🔬 DEEP DIVE", "🖥️ SCREENER", "📚 ACCOUNTING", "💳 ASSINATURA"]
if USER == 'admin': menu.append("👑 ADMIN")
op = st.sidebar.radio("MÓDULOS", menu)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 SYNC DADOS"):
    with st.spinner("Conectando feeds..."):
        wl = vault.carregar_config('watchlist', "PETR4.SA,VALE3.SA,ITUB4.SA,BTC-USD", user_id=UID)
        l = [x.strip() for x in wl.split(',')]
        st.session_state['df'] = db.buscar_dados_multiticker(l, "1y")
        st.session_state['macro'] = governor.coletar_dados_macro()
    st.rerun()

if st.sidebar.button("🚪 SAIR"):
    st.session_state.clear(); st.rerun()

# --- APP LOGIC ---
if 'df' in st.session_state:
    df = st.session_state['df']; macro = st.session_state['macro']
    render_ticker(df)
    
    if op == "🏠 DASHBOARD":
        st.subheader("Market Overview")
        c1, c2, c3 = st.columns(3)
        if not macro.empty:
            l = macro.iloc[-1]
            c1.metric("S&P 500", f"{l['Equities (S&P 500)']:,.0f}")
            c2.metric("Dólar (DXY)", f"{l['Dollar (DXY)']:.2f}")
            c3.metric("VIX (Risco)", f"{l['Volatility (VIX)']:.2f}")
        
        st.markdown("### 📊 Performance Recente")
        st.line_chart(df/df.iloc[0]*100)

    elif op == "🧠 WAR ROOM":
        st.header("🧠 WAR ROOM (QUANT ANALYSIS)")
        
        # VISUAL IGUAL AO DO CHATGPT (Histograma & Estatística)
        if IS_PRO:
            t1, t2, t3 = st.tabs(["DISTRIBUIÇÃO DE RETORNOS", "RISCO x RETORNO", "BACKTEST"])
            
            with t1:
                st.subheader("Histograma de Retornos Diários")
                # Selecionar ativo para o histograma
                asset_hist = st.selectbox("Selecione Ativo", df.columns)
                returns = df[asset_hist].pct_change().dropna()
                
                # Gráfico de Histograma Profissional (Plotly)
                fig_hist = px.histogram(returns, x=asset_hist, nbins=50, title=f"Distribuição Normal - {asset_hist}",
                                      color_discrete_sequence=['#00e5ff'])
                fig_hist.update_layout(template='plotly_dark', showlegend=False, bargap=0.1)
                st.plotly_chart(fig_hist, use_container_width=True)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Média Diária", f"{returns.mean()*100:.2f}%")
                c2.metric("Volatilidade (Std)", f"{returns.std()*100:.2f}%")
                c3.metric("Kurtosis", f"{returns.kurtosis():.2f}")

            with t2:
                st.subheader("Fronteira Eficiente (Risco x Retorno)")
                # Scatter Plot igual ao do print
                ret_anual = df.pct_change().mean() * 252 * 100
                vol_anual = df.pct_change().std() * (252**0.5) * 100
                df_scat = pd.DataFrame({'Retorno': ret_anual, 'Volatilidade': vol_anual, 'Ativo': df.columns})
                
                fig_scat = px.scatter(df_scat, x='Volatilidade', y='Retorno', text='Ativo', color='Retorno',
                                    color_continuous_scale='RdYlGn', size_max=60)
                fig_scat.update_traces(textposition='top center', marker=dict(size=20))
                fig_scat.update_layout(template='plotly_dark', height=500)
                st.plotly_chart(fig_scat, use_container_width=True)

            with t3:
                st.subheader("Backtest de Estratégia")
                if st.button("RODAR BACKTEST RSI"):
                     res, _, ret, _ = timemachine.rodar_backtest(db.buscar_dados_detalhados(df.columns[0], "2y"), "RSI (Reversão)")
                     st.line_chart(res['Strategy_Equity'])
                     st.success(f"Resultado Final: {ret:.2f}%")
        else:
            # TEASER: Mostra o gráfico borrado
            st.markdown("<div class='blur'>", unsafe_allow_html=True)
            st.bar_chart(np.random.randn(50, 3))
            st.markdown("</div>", unsafe_allow_html=True)
            render_paywall("WAR ROOM QUANT")

    elif op == "🧪 CRYPTO LAB":
        if IS_PRO:
            st.header("CRYPTO INTELLIGENCE")
            c1, c2 = st.columns([3, 1])
            with c1:
                if 'BTC-USD' in df:
                    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['BTC-USD'], close=df['BTC-USD'], high=df['BTC-USD'], low=df['BTC-USD'])])
                    fig.update_layout(template='plotly_dark', title="Bitcoin Price Action")
                    st.plotly_chart(fig, use_container_width=True)
                else: st.warning("Adicione BTC-USD na Watchlist")
            with c2:
                st.metric("Fear & Greed", "72 (Greed)")
                st.metric("BTC Dominance", "54.1%")
                st.progress(54)
        else: render_paywall("CRYPTO LAB")
        
    elif op == "🖥️ SCREENER":
        st.header("MARKET SCREENER")
        if IS_PRO:
            if st.button("ESCANEAR MERCADO"):
                scan = hunter.escanear_estrategias(df)
                if not scan.empty: st.dataframe(scan, use_container_width=True)
                else: st.info("Nenhum setup encontrado.")
            st.dataframe(df.tail(5))
        else: render_paywall("SCREENER")

    elif op == "🔬 DEEP DIVE":
        st.header("DEEP DIVE ANALYSIS")
        a = st.selectbox("Ativo", df.columns)
        if IS_PRO:
            d = db.buscar_dados_detalhados(a, "1y")
            p, _, s = oracle.prever_tendencia_ml(a, d)
            st.metric("IA Prediction", s, f"{p:.1f}% confidence")
            st.line_chart(d['Close'])
        else: render_paywall("DEEP DIVE")

    elif op == "💳 ASSINATURA":
        st.header("Sua Assinatura")
        if IS_PRO:
            st.success(f"Você é membro {PLANO}. Aproveite o terminal.")
        else:
            st.info("Você está no plano Gratuito.")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🟢 Plano Soldato")
                st.markdown("Acesso total à War Room, Scanner e IA.")
                url = criar_checkout(UID, f"user_{UID}@email.com")
                st.link_button("ASSINAR (R$ 97,90)", url, type="primary")
            with c2:
                st.markdown("### Benefícios")
                st.markdown("- Dados em Tempo Real (Delay 15min)\n- Histograma de Risco\n- Scanner Automático")

    elif op == "👑 ADMIN":
        st.header("Admin Panel")
        c = vault.get_connection()
        users = pd.read_sql("SELECT * FROM usuarios", c)
        st.dataframe(users)
        u = st.selectbox("User", users['username'].unique())
        if st.button("Tornar Soldato"):
            cur = c.cursor()
            cur.execute("UPDATE usuarios SET plano='Soldato' WHERE username=?", (u,))
            c.commit(); c.close(); st.success("Feito!")

else: st.info("Clique em **SYNC DADOS** na lateral para carregar o mercado.")