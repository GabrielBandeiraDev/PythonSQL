import flet as ft
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import io

# Conectar ao banco de dados SQLite
def conectar_db():
    return sqlite3.connect('vendas.db')

# Função para cadastrar uma venda
def cadastrar_venda(categoria_id, valor, data):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO vendas (categoria_id, valor, data)
                      VALUES (?, ?, ?)''', (categoria_id, valor, data))
    conn.commit()
    conn.close()

# Função para cadastrar um produto
def cadastrar_produto(nome, preco):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO categorias (nome)
                      VALUES (?)''', (nome,))
    conn.commit()
    conn.close()

# Função para gerar um relatório de vendas
def relatorio_vendas():
    conn = conectar_db()
    query = '''
    SELECT c.nome AS categoria, COUNT(v.id) AS total_vendas, SUM(v.valor) AS total_valor, 
           AVG(v.valor) AS media_valor
    FROM vendas v
    JOIN categorias c ON v.categoria_id = c.id
    GROUP BY c.nome
    '''
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Função para gerar gráficos
def gerar_grafico_vendas():
    df = relatorio_vendas()
    fig, ax = plt.subplots()
    df.plot(kind='bar', x='categoria', y='total_valor', ax=ax, title="Vendas por Categoria", color='#4e73df')
    ax.set_xlabel('Categoria')
    ax.set_ylabel('Total de Vendas (R$)')
    plt.tight_layout()

    # Salvar o gráfico em um arquivo de imagem
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return img

# Função para média de vendas diárias
def media_vendas_diarias():
    conn = conectar_db()
    query = '''
    SELECT DATE(data) AS data_venda, COUNT(id) AS total_vendas, SUM(valor) AS total_valor
    FROM vendas
    GROUP BY data_venda
    ORDER BY data_venda
    '''
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Função para gerar gráfico de média de vendas diárias
def gerar_grafico_media_diaria():
    df = media_vendas_diarias()
    fig, ax = plt.subplots()
    df.plot(x='data_venda', y='total_valor', ax=ax, kind='line', title="Média de Vendas Diárias", color='#f6c23e')
    ax.set_xlabel('Data')
    ax.set_ylabel('Total de Vendas (R$)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Salvar o gráfico em um arquivo de imagem
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return img

# Função para a interface gráfica com Flet
def main(page: ft.Page):
    page.title = "Sistema de Análise de Vendas"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE

    # Estilos de texto e componentes
    titulo = ft.Text("Bem-vindo ao Sistema de Análise de Vendas", style="headlineMedium", color=ft.Colors.INDIGO)

    # Campos de cadastro de venda
    categoria_input = ft.TextField(label="Categoria da Venda", autofocus=True, color=ft.Colors.BLACK, border_color=ft.Colors.INDIGO, border_radius=10, width=300)
    valor_input = ft.TextField(label="Valor da Venda", keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.BLACK, border_color=ft.Colors.INDIGO, border_radius=10, width=300)
    data_input = ft.TextField(label="Data da Venda (YYYY-MM-DD)", keyboard_type=ft.KeyboardType.DATETIME, color=ft.Colors.BLACK, border_color=ft.Colors.INDIGO, border_radius=10, width=300)

    # Campos para cadastrar produto
    produto_input = ft.TextField(label="Nome do Produto", color=ft.Colors.BLACK, border_color=ft.Colors.INDIGO, border_radius=10, width=300)  
    preco_input = ft.TextField(label="Preço do Produto (R$)", keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.BLACK, border_color=ft.Colors.INDIGO, border_radius=10, width=300)

    # Função de cadastro de venda
    def on_cadastrar_venda(e):
        categoria = categoria_input.value
        valor = float(valor_input.value)
        data = data_input.value
        
        if not data:
            page.add(ft.Text("A data da venda não pode estar vazia!", color=ft.Colors.RED))
            return
        
        try:
            data = datetime.strptime(data, "%Y-%m-%d").date()
        except ValueError:
            page.add(ft.Text("Formato de data inválido. Use o formato YYYY-MM-DD.", color=ft.Colors.RED))
            return

        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM categorias WHERE nome = ?', (categoria,))
        categoria_id = cursor.fetchone()
        if categoria_id:
            categoria_id = categoria_id[0]
            cadastrar_venda(categoria_id, valor, data)
            page.add(ft.Text(f"Venda cadastrada: {categoria} - R${valor} - {data}", color=ft.Colors.GREEN))
        else:
            page.add(ft.Text(f"Categoria '{categoria}' não encontrada!", color=ft.Colors.RED))
        conn.close()

    # Função de cadastro de produto
    def on_cadastrar_produto(e):
        nome = produto_input.value
        preco = float(preco_input.value)

        cadastrar_produto(nome, preco)
        page.add(ft.Text(f"Produto cadastrado: {nome} - R${preco:.2f}", color=ft.Colors.GREEN))

    # Função para gerar relatório
    def on_gerar_relatorio(e):
        df = relatorio_vendas()
        page.add(ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Categoria")),
            ft.DataColumn(ft.Text("Total de Vendas")),
            ft.DataColumn(ft.Text("Total Valor (R$)")),
            ft.DataColumn(ft.Text("Média Valor (R$)"))
        ], rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(row["categoria"])),
                ft.DataCell(ft.Text(str(row["total_vendas"]))),
                ft.DataCell(ft.Text(f"R${row['total_valor']:.2f}")),
                ft.DataCell(ft.Text(f"R${row['media_valor']:.2f}"))
            ]) for index, row in df.iterrows()
        ]))

    # Função para exibir gráficos
    def on_gerar_grafico_vendas(e):
        img = gerar_grafico_vendas()
        page.add(ft.Image(src=img))

    def on_gerar_grafico_media_diaria(e):
        img = gerar_grafico_media_diaria()
        page.add(ft.Image(src=img))

    # Botões e componentes
    cadastrar_venda_button = ft.ElevatedButton("Cadastrar Venda", on_click=on_cadastrar_venda, color=ft.Colors.WHITE, bgcolor=ft.Colors.INDIGO, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))
    cadastrar_produto_button = ft.ElevatedButton("Cadastrar Produto", on_click=on_cadastrar_produto, color=ft.Colors.WHITE, bgcolor=ft.Colors.INDIGO, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))
    relatorio_button = ft.ElevatedButton("Gerar Relatório", on_click=on_gerar_relatorio, color=ft.Colors.WHITE, bgcolor=ft.Colors.INDIGO, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))
    grafico_vendas_button = ft.ElevatedButton("Gerar Gráfico de Vendas", on_click=on_gerar_grafico_vendas, color=ft.Colors.WHITE, bgcolor=ft.Colors.INDIGO, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))
    grafico_media_diaria_button = ft.ElevatedButton("Gerar Gráfico de Média Diária", on_click=on_gerar_grafico_media_diaria, color=ft.Colors.WHITE, bgcolor=ft.Colors.INDIGO, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))

    # Adicionando os componentes à página
    page.add(
        ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                titulo,
                categoria_input,
                valor_input,
                data_input,
                cadastrar_venda_button,
                ft.Divider(),
                produto_input,
                preco_input,
                cadastrar_produto_button,
                ft.Divider(),
                relatorio_button,
                grafico_vendas_button,
                grafico_media_diaria_button
            ]
        )
    )

# Executar a aplicação Flet
ft.app(target=main)
