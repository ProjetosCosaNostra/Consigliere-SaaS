# Arquivo: E:\Consigliere\src\utils.py
# Módulo: Shared Utilities (O Cinto de Utilidades)

import streamlit as st
import pandas as pd
import dados as db
import database as vault
import macro as governor
import time
import os
import io

# --- CONFIGURAÇÃO VISUAL (CSS) ---
def carregar_css():
    st.markdown("""
    <style>
        .stApp { background-color: #000000; color: #E0E0E0; }
        h1, h2, h3 { font-family: 'Roboto', sans-serif; color: #D4AF37; letter-spacing: 1px; text-transform: uppercase; }
        .stMetricValue { font-weight: bold; color: #D4AF37 !important; font-family: 'Consolas', monospace; }
        div[data-testid="stExpander"] { background-color: #111; border: 1px solid #333; }
        .stDataFrame { font-family: 'Consolas', monospace; }
        div.stButton > button { font-weight: bold; border-radius: 5px; border: 1px solid #333; background-color: #1e1e1e; color: white; transition: all 0.3s; }
        div.stButton > button:hover { border-color: #D4AF37; color: #D4AF37; }
        .risk-box { border-left: 3px solid #FF4B4B; padding-left: 10px; margin-bottom: 15px; background-color: #1a0505; }
        .status-ok { color: #00FF00; border: 1px solid #00FF00; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.8em; }
        .status-warn { color: #FFA500; border: 1px solid #FFA500; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS (CACHEADO) ---
@st.cache_data(ttl=3600, show_spinner=False)
def carregar_dados_sistema(lista_ativos, periodo):
    df_p = db.buscar_dados_multiticker(lista_ativos, periodo)
    df_m = governor.coletar_dados_macro()
    return df_p, df_m

# --- AUXILIARES ---
def checar_status_sentinela():
    try:
        if not os.path.exists("heartbeat.txt"): return False, "Nunca Iniciada"
        with open("heartbeat.txt", "r") as f: last_beat = float(f.read())
        if (time.time() - last_beat) < 2400: return True, "Online"
        return False, "Offline"
    except: return False, "Erro"

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df.to_excel(writer, index=False)
    return output.getvalue()

def inicializar_estado():
    vault.init_db()
    if 'portfolio' not in st.session_state: st.session_state['portfolio'] = vault.carregar_portfolio()
    if 'historico' not in st.session_state: st.session_state['historico'] = vault.carregar_historico()
    # Carrega configs globais
    if 'watchlist' not in st.session_state: 
        st.session_state['watchlist'] = vault.carregar_config('watchlist', "PETR4.SA, VALE3.SA, BTC-USD")