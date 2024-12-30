import sqlite3

def criar_db():
    # Conecta ou cria o banco de dados
    conn = sqlite3.connect('vendas.db')
    cursor = conn.cursor()

    # Criação da tabela de Categorias
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )''')

    # Criação da tabela de Produtos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL
    )''')

    # Criação da tabela de Grupos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS grupos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )''')

    # Criação da tabela de Vendas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria_id INTEGER,
        valor REAL NOT NULL,
        data DATE NOT NULL,
        FOREIGN KEY (categoria_id) REFERENCES categorias (id)
    )''')

    # Criação da tabela de vínculo de Produtos a Grupos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos_grupos (
        produto_id INTEGER,
        grupo_id INTEGER,
        FOREIGN KEY (produto_id) REFERENCES produtos (id),
        FOREIGN KEY (grupo_id) REFERENCES grupos (id),
        PRIMARY KEY (produto_id, grupo_id)
    )''')

    # Commit e fechamento da conexão
    conn.commit()
    conn.close()

# Chama a função para criar o banco de dados e as tabelas
criar_db()
