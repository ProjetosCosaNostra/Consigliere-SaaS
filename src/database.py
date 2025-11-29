# Arquivo: E:\Consigliere\src\database.py
# Módulo: The Vault (SaaS Edition - Multi-Tenant)
# Status: Production Ready

import sqlite3
import pandas as pd
from datetime import datetime
import time
import hashlib
import os

DB_PATH = "consigliere.db"

def get_connection(max_retries=5, delay=0.5):
    """
    Conecta ao banco SQLite com retries e modo WAL.
    Ideal para concorrência local.
    """
    retry_count = 0
    while retry_count < max_retries:
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            conn.execute("PRAGMA journal_mode=WAL;")
            return conn
        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                time.sleep(delay)
                retry_count += 1
            else:
                raise e
    raise Exception("Banco de dados travado após várias tentativas.")

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # --- TABELAS BASE (Multi-Tenant) ---
    
    # 1. Usuários
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    senha_hash TEXT,
                    plano TEXT DEFAULT 'Associado',
                    criado_em TEXT
                )''')

    # 2. Portfolio (Vinculado ao user_id)
    c.execute('''CREATE TABLE IF NOT EXISTS portfolio (
                    user_id INTEGER DEFAULT 1,
                    ativo TEXT,
                    qtd REAL,
                    preco_medio REAL,
                    tipo TEXT,
                    stop_loss REAL DEFAULT 0,
                    take_profit REAL DEFAULT 0,
                    PRIMARY KEY (user_id, ativo),
                    FOREIGN KEY(user_id) REFERENCES usuarios(id)
                )''')

    # 3. Trades (Vinculado ao user_id)
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    data TEXT,
                    ativo TEXT,
                    operacao TEXT,
                    qtd REAL,
                    preco REAL,
                    total REAL,
                    nota TEXT,
                    pnl_realizado REAL DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES usuarios(id)
                )''')
    
    # 4. Configurações (Tokens Telegram por user)
    c.execute('''CREATE TABLE IF NOT EXISTS config (
                    user_id INTEGER DEFAULT 1,
                    chave TEXT,
                    valor TEXT,
                    PRIMARY KEY (user_id, chave)
                )''')

    # 5. Metas de Alocação
    c.execute('''CREATE TABLE IF NOT EXISTS metas (
                    user_id INTEGER DEFAULT 1,
                    ativo TEXT,
                    target_pct REAL,
                    PRIMARY KEY (user_id, ativo)
                )''')

    # 6. Sinais
    c.execute('''CREATE TABLE IF NOT EXISTS sinais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    data TEXT,
                    ativo TEXT,
                    setup TEXT,
                    preco_no_sinal REAL,
                    status TEXT DEFAULT 'Ativo'
                )''')

    # --- MIGRAÇÃO DE LEGADO (Se existir banco antigo single-player) ---
    try:
        # Se tabela existe mas não tem user_id, adiciona
        c.execute("SELECT user_id FROM portfolio LIMIT 1")
    except:
        try: c.execute("ALTER TABLE portfolio ADD COLUMN user_id INTEGER DEFAULT 1")
        except: pass
        try: c.execute("ALTER TABLE trades ADD COLUMN user_id INTEGER DEFAULT 1")
        except: pass
        try: c.execute("ALTER TABLE config ADD COLUMN user_id INTEGER DEFAULT 1")
        except: pass
        try: c.execute("ALTER TABLE metas ADD COLUMN user_id INTEGER DEFAULT 1")
        except: pass
        try: c.execute("ALTER TABLE sinais ADD COLUMN user_id INTEGER DEFAULT 1")
        except: pass

    # Cria ADMIN padrão (user_id=1) se não existir
    c.execute("SELECT * FROM usuarios WHERE id = 1")
    if not c.fetchone():
        pass_hash = hashlib.sha256("admin123".encode()).hexdigest()
        dt = datetime.now().strftime("%Y-%m-%d")
        c.execute("INSERT INTO usuarios (id, username, senha_hash, plano, criado_em) VALUES (1, 'admin', ?, 'Capo', ?)", (pass_hash, dt))
        # Inicializa Caixa do Admin
        c.execute("INSERT OR IGNORE INTO portfolio (user_id, ativo, qtd, preco_medio, tipo) VALUES (1, 'Caixa', 100000.0, 1.0, 'Fiat')")

    conn.commit()
    conn.close()

# --- FUNÇÕES DE USUÁRIO ---
def criar_usuario(username, senha, plano="Associado"):
    conn = get_connection()
    c = conn.cursor()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    criado_em = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        c.execute("INSERT INTO usuarios (username, senha_hash, plano, criado_em) VALUES (?, ?, ?, ?)", (username, senha_hash, plano, criado_em))
        uid = c.lastrowid
        # Caixa Inicial
        c.execute("INSERT INTO portfolio (user_id, ativo, qtd, preco_medio, tipo) VALUES (?, 'Caixa', 100000.0, 1.0, 'Fiat')", (uid,))
        conn.commit()
        return True, "Usuário criado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Nome de usuário já existe."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def verificar_login(username, senha):
    conn = get_connection()
    c = conn.cursor()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    c.execute("SELECT id, plano FROM usuarios WHERE username = ? AND senha_hash = ?", (username, senha_hash))
    res = c.fetchone()
    conn.close()
    return res # (id, plano)

# --- FUNÇÕES DE NEGÓCIO (Com user_id) ---

def carregar_portfolio(user_id=1):
    conn = get_connection()
    try: 
        df = pd.read_sql("SELECT * FROM portfolio WHERE user_id = ?", conn, params=(user_id,))
    except: 
        df = pd.DataFrame()
    conn.close()
    
    port = {}
    if not df.empty:
        for _, row in df.iterrows():
            if row['ativo'] == 'Caixa': port['Caixa'] = row['qtd']
            else: port[row['ativo']] = {'qtd': row['qtd'], 'pm': row['preco_medio'], 'stop': row['stop_loss'], 'take': row['take_profit']}
    return port

def carregar_historico(user_id=1):
    conn = get_connection()
    try: 
        df = pd.read_sql("SELECT * FROM trades WHERE user_id = ? ORDER BY id DESC", conn, params=(user_id,))
    except: 
        df = pd.DataFrame()
    conn.close()
    
    hist = []
    if not df.empty:
        for _, row in df.iterrows():
            hist.append({"Data": row['data'], "Ativo": row['ativo'], "Op": row['operacao'], "Qtd": row['qtd'], "Preço": row['preco'], "Nota": row['nota'], "PnL": row['pnl_realizado']})
    return hist

def registrar_trade(ativo, operacao, qtd, preco, nota="", stop=0, take=0, user_id=1):
    conn = get_connection()
    c = conn.cursor()
    data_hora = datetime.now().strftime("%d/%m %H:%M")
    total = qtd * preco; pnl = 0.0
    
    # Busca dados DO USUÁRIO
    c.execute("SELECT qtd, preco_medio FROM portfolio WHERE user_id = ? AND ativo = ?", (user_id, ativo))
    pos = c.fetchone()
    c.execute("SELECT qtd FROM portfolio WHERE user_id = ? AND ativo = 'Caixa'", (user_id,))
    res_caixa = c.fetchone()
    cx = res_caixa[0] if res_caixa else 0.0
    
    if operacao == 'C':
        # Debita Caixa
        c.execute("UPDATE portfolio SET qtd = ? WHERE user_id = ? AND ativo = 'Caixa'", (cx - total, user_id))
        if pos:
            nq = pos[0] + qtd; npm = ((pos[0]*pos[1])+(qtd*preco))/nq
            c.execute("UPDATE portfolio SET qtd=?, preco_medio=?, stop_loss=?, take_profit=? WHERE user_id=? AND ativo=?", (nq, npm, stop, take, user_id, ativo))
        else:
            c.execute("INSERT INTO portfolio (user_id, ativo, qtd, preco_medio, tipo, stop_loss, take_profit) VALUES (?, ?, ?, ?, ?, ?, ?)", (user_id, ativo, qtd, preco, 'Stock', stop, take))
            
    elif operacao == 'V':
        # Credita Caixa
        c.execute("UPDATE portfolio SET qtd = ? WHERE user_id = ? AND ativo = 'Caixa'", (cx + total, user_id))
        if pos:
            pnl = (preco - pos[1]) * qtd
            nq = pos[0] - qtd
            if nq <= 0.0001: c.execute("DELETE FROM portfolio WHERE user_id = ? AND ativo = ?", (user_id, ativo))
            else: c.execute("UPDATE portfolio SET qtd = ? WHERE user_id = ? AND ativo = ?", (nq, user_id, ativo))
            
    c.execute("INSERT INTO trades (user_id, data, ativo, operacao, qtd, preco, total, nota, pnl_realizado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, data_hora, ativo, operacao, qtd, preco, total, nota, pnl))
    conn.commit(); conn.close()

def registrar_sinal(ativo, setup, preco, user_id=1):
    conn = get_connection()
    c = conn.cursor()
    hoje = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT id FROM sinais WHERE user_id=? AND ativo=? AND setup=? AND data LIKE ?", (user_id, ativo, setup, f"{hoje}%"))
    if c.fetchone(): conn.close(); return False
    
    agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO sinais (user_id, data, ativo, setup, preco_no_sinal) VALUES (?, ?, ?, ?, ?)", (user_id, agora, ativo, setup, preco))
    conn.commit(); conn.close(); return True

def carregar_sinais(user_id=1):
    conn = get_connection()
    try: df = pd.read_sql("SELECT * FROM sinais WHERE user_id=? ORDER BY id DESC LIMIT 50", conn, params=(user_id,))
    except: df = pd.DataFrame()
    conn.close(); return df

# --- CONFIGS & METAS POR USUÁRIO ---
def salvar_config(chave, valor, user_id=1):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (user_id, chave, valor) VALUES (?, ?, ?)", (user_id, chave, str(valor)))
    conn.commit(); conn.close()

def carregar_config(chave, valor_padrao="", user_id=1):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT valor FROM config WHERE user_id=? AND chave=?", (user_id, chave))
    res = c.fetchone(); conn.close()
    return res[0] if res else valor_padrao

def salvar_meta(ativo, pct, user_id=1):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO metas (user_id, ativo, target_pct) VALUES (?, ?, ?)", (user_id, ativo, pct))
    conn.commit(); conn.close()

def carregar_metas(user_id=1):
    conn = get_connection()
    try: df = pd.read_sql("SELECT * FROM metas WHERE user_id=?", conn, params=(user_id,))
    except: df = pd.DataFrame()
    conn.close()
    if df.empty: return {}
    return dict(zip(df['ativo'], df['target_pct']))