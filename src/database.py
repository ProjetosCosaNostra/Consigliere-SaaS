# Arquivo: E:\Consigliere\src\database.py
# Status: Fixed - V3 Structure (Clean Slate)

import sqlite3
import pandas as pd
import hashlib
from datetime import datetime
import time

DB_PATH = "consigliere.db"

def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn
    except:
        time.sleep(1)
        return sqlite3.connect(DB_PATH, timeout=10)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # TABELA NOVA V3 (Para corrigir o erro de coluna)
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios_v3 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    senha_hash TEXT,
                    plano TEXT DEFAULT 'Associado',
                    created_at TEXT,
                    stripe_id TEXT,
                    assinatura_status TEXT DEFAULT 'inactive'
                )''')

    # Tabelas de Dados
    c.execute('''CREATE TABLE IF NOT EXISTS portfolio (
                    user_id INTEGER, 
                    ativo TEXT, 
                    qtd REAL, 
                    preco_medio REAL, 
                    tipo TEXT,
                    stop_loss REAL DEFAULT 0, 
                    take_profit REAL DEFAULT 0,
                    PRIMARY KEY (user_id, ativo)
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    user_id INTEGER, 
                    data TEXT, 
                    ativo TEXT, 
                    operacao TEXT, 
                    qtd REAL, 
                    preco REAL, 
                    total REAL, 
                    nota TEXT, 
                    pnl_realizado REAL DEFAULT 0
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS config (user_id INTEGER, chave TEXT, valor TEXT, PRIMARY KEY(user_id, chave))''')
    
    # Garante Admin
    c.execute("SELECT * FROM usuarios_v3 WHERE username = 'admin'")
    if not c.fetchone():
        ph = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO usuarios_v3 (username, senha_hash, plano, created_at) VALUES (?, ?, ?, ?)", 
                  ('admin', ph, 'Capo', datetime.now().strftime("%Y-%m-%d")))

    conn.commit()
    conn.close()

# --- FUNÇÕES V3 ---
def criar_usuario(u, p):
    try:
        conn = get_connection(); c = conn.cursor()
        ph = hashlib.sha256(p.encode()).hexdigest()
        dt = datetime.now().strftime("%Y-%m-%d")
        c.execute("INSERT INTO usuarios_v3 (username, senha_hash, created_at) VALUES (?, ?, ?)", (u, ph, dt))
        uid = c.lastrowid
        c.execute("INSERT OR IGNORE INTO portfolio (user_id, ativo, qtd, preco_medio, tipo) VALUES (?, 'Caixa', 100000.0, 1.0, 'Fiat')", (uid,))
        conn.commit(); conn.close()
        return True, "Sucesso"
    except sqlite3.IntegrityError: return False, "Usuário já existe"
    except Exception as e: return False, str(e)

def verificar_login(u, p):
    conn = get_connection(); c = conn.cursor()
    ph = hashlib.sha256(p.encode()).hexdigest()
    c.execute("SELECT id, plano FROM usuarios_v3 WHERE username=? AND senha_hash=?", (u, ph))
    res = c.fetchone(); conn.close()
    return res

# Mantendo compatibilidade das outras funções
def carregar_portfolio(uid):
    conn = get_connection()
    try: df = pd.read_sql("SELECT * FROM portfolio WHERE user_id=?", conn, params=(uid,))
    except: df = pd.DataFrame()
    conn.close()
    port = {}
    if not df.empty:
        for _, r in df.iterrows():
            if r['ativo'] == 'Caixa': port['Caixa'] = r['qtd']
            else: port[r['ativo']] = {'qtd':r['qtd'], 'pm':r['preco_medio']}
    return port

def carregar_historico(uid):
    conn = get_connection()
    try: df = pd.read_sql("SELECT * FROM trades WHERE user_id=? ORDER BY id DESC", conn, params=(uid,))
    except: df = pd.DataFrame()
    conn.close()
    hist = []
    if not df.empty:
        for _, r in df.iterrows():
            hist.append({'Data':r['data'], 'Ativo':r['ativo'], 'Op':r['operacao'], 'Qtd':r['qtd'], 'Preço':r['preco'], 'PnL':r['pnl_realizado']})
    return hist

def registrar_trade(atv, op, qtd, pr, nota, stop=0, take=0, user_id=1):
    conn = get_connection(); c = conn.cursor()
    dt = datetime.now().strftime("%d/%m %H:%M"); tot = qtd*pr; pnl=0
    c.execute("SELECT qtd, preco_medio FROM portfolio WHERE user_id=? AND ativo=?", (user_id, atv))
    pos = c.fetchone()
    c.execute("SELECT qtd FROM portfolio WHERE user_id=? AND ativo='Caixa'", (user_id,))
    cx_res = c.fetchone(); cx = cx_res[0] if cx_res else 0
    
    if op == 'C':
        c.execute("UPDATE portfolio SET qtd=? WHERE user_id=? AND ativo='Caixa'", (cx-tot, user_id))
        if pos:
            nq = pos[0]+qtd; npm = ((pos[0]*pos[1])+(qtd*pr))/nq
            c.execute("UPDATE portfolio SET qtd=?, preco_medio=? WHERE user_id=? AND ativo=?", (nq, npm, user_id, atv))
        else:
            c.execute("INSERT INTO portfolio (user_id, ativo, qtd, preco_medio, tipo) VALUES (?, ?, ?, ?, 'Stock')", (user_id, atv, qtd, pr))
    elif op == 'V':
        c.execute("UPDATE portfolio SET qtd=? WHERE user_id=? AND ativo='Caixa'", (cx+tot, user_id))
        if pos:
            pnl = (pr - pos[1]) * qtd
            nq = pos[0]-qtd
            if nq <= 0.0001: c.execute("DELETE FROM portfolio WHERE user_id=? AND ativo=?", (user_id, atv))
            else: c.execute("UPDATE portfolio SET qtd=? WHERE user_id=? AND ativo=?", (nq, user_id, atv))
            
    c.execute("INSERT INTO trades (user_id, data, ativo, operacao, qtd, preco, total, nota, pnl_realizado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
              (user_id, dt, atv, op, qtd, pr, tot, nota, pnl))
    conn.commit(); conn.close()

def carregar_config(k, d, user_id):
    conn = get_connection(); c = conn.cursor()
    c.execute("SELECT valor FROM config WHERE user_id=? AND chave=?", (user_id, k))
    r = c.fetchone(); conn.close()
    return r[0] if r else d

def salvar_config(k, v, user_id):
    conn = get_connection(); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (user_id, chave, valor) VALUES (?, ?, ?)", (user_id, k, str(v)))
    conn.commit(); conn.close()