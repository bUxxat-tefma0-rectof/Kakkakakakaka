import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        nome_empresa TEXT,
        responsavel TEXT,
        whatsapp TEXT,
        instagram TEXT,
        site TEXT,
        nicho TEXT,
        objetivo TEXT,
        data_cadastro TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS solicitacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        descricao TEXT,
        logo_path TEXT,
        midia_path TEXT,
        status TEXT DEFAULT 'Em análise',
        observacao TEXT,
        data TEXT
    )''')
    
    conn.commit()
    conn.close()

def salvar_cliente(telegram_id, dados):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO clientes 
                 (telegram_id, nome_empresa, responsavel, whatsapp, instagram, site, nicho, objetivo, data_cadastro)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (telegram_id, dados['nome_empresa'], dados['responsavel'], dados['whatsapp'],
               dados['instagram'], dados.get('site'), dados['nicho'], dados['objetivo'], datetime.now().isoformat()))
    conn.commit()
    cliente_id = c.lastrowid
    conn.close()
    return cliente_id

def salvar_solicitacao(cliente_id, descricao, logo_path=None, midia_path=None):
    conn = sqlite3.connect('clientes.db')
    c = conn.cursor()
    c.execute('''INSERT INTO solicitacoes 
                 (cliente_id, descricao, logo_path, midia_path, data)
                 VALUES (?, ?, ?, ?, ?)''',
              (cliente_id, descricao, logo_path, midia_path, datetime.now().isoformat()))
    solicitacao_id = c.lastrowid
    conn.commit()
    conn.close()
    return solicitacao_id
