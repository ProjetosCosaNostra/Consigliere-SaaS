import os
import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "consigliere.db"

# Apaga o banco antigo se existir
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("💀 Banco de dados antigo deletado.")

# Cria um novo do zero
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Tabela Usuários
c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                senha_hash TEXT,
                plano TEXT DEFAULT 'Associado',
                created_at TEXT,
                stripe_id TEXT,
                assinatura_status TEXT DEFAULT 'inactive'
            )''')

# Tabela Licenças
c.execute('''CREATE TABLE IF NOT EXISTS licencas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave TEXT UNIQUE,
                plano TEXT,
                dias_validade INTEGER,
                status TEXT DEFAULT 'Ativa',
                criado_em TEXT
            )''')

# Tabelas de Negócio
c.execute('CREATE TABLE IF NOT EXISTS portfolio (user_id INTEGER, ativo TEXT, qtd REAL, preco_medio REAL, tipo TEXT, PRIMARY KEY(user_id, ativo))')
c.execute('CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, data TEXT, ativo TEXT, operacao TEXT, qtd REAL, preco REAL, total REAL, nota TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS config (user_id INTEGER, chave TEXT, valor TEXT, PRIMARY KEY(user_id, chave))')

# Cria Admin Padrão
senha_admin = hashlib.sha256("admin123".encode()).hexdigest()
c.execute("INSERT INTO usuarios (username, senha_hash, plano, created_at) VALUES (?, ?, ?, ?)", 
          ('admin', senha_admin, 'Capo', datetime.now().strftime("%Y-%m-%d")))

conn.commit()
conn.close()

print("✅ Novo Banco criado com sucesso.")
print("🔑 Login Admin: admin / admin123")