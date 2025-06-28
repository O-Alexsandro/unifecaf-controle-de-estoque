import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import bcrypt
from datetime import datetime

# ==============================================
# BANCO DE DADOS
# ==============================================

def connect_db():
    """
    Cria e retorna uma conexão com o banco de dados SQLite
    Cria as tabelas se não existirem:
    - usuarios: armazena os usuários do sistema
    - produtos: cadastro de itens do estoque
    - movimentacoes: histórico de entradas/saídas
    """
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()
    
    # Tabela de usuários (admin/comum)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            perfil TEXT
        )
    ''')
    
    # Tabela de produtos em estoque
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT UNIQUE,
            quantidade INTEGER,
            quantidade_minima INTEGER
        )
    ''')
    
    # Tabela de histórico de movimentações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY,
            produto_id INTEGER,
            tipo TEXT,
            quantidade INTEGER,
            data TEXT,
            usuario TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    ''')
    
    conn.commit()
    return conn

def criar_usuario_padrao():
    """
    Cria o usuário admin padrão se não existir
    Login: admin
    Senha: admin123 (criptografada)
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Usa INSERT OR IGNORE para evitar duplicação
        cursor.execute(
            "INSERT OR IGNORE INTO usuarios (username, password, perfil) VALUES (?, ?, ?)",
            ("admin", bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8'), "Administrador")
        )
        conn.commit()
    finally:
        conn.close()

# ==============================================
# INTERFACE GRÁFICA
# ==============================================

class ControleEstoqueApp:
    def __init__(self):
        """Inicializa a aplicação com configurações básicas"""
        self.root = tk.Tk()
        self.root.title("Controle de Estoque v3.0")
        self.root.geometry("1100x750")
        self.current_user = None  # Armazena o usuário logado
        self.produto_selecionado = None  # Produto selecionado para edição
        
        # Configurações iniciais
        criar_usuario_padrao()
        self._configurar_estilos()
        self._mostrar_tela_login()

    def _configurar_estilos(self):
        """Configura os temas e estilos visuais da interface"""
        style = ttk.Style()
        style.theme_use('clam')  # Tema moderno
        
        # Estilos personalizados
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Red.TLabel', foreground='red', font=('Arial', 10, 'bold'))
        style.configure('Red.TButton', foreground='white', background='#d9534f')  # Botão vermelho para ações perigosas
        style.configure('Treeview', rowheight=25)  # Altura das linhas nas tabelas
        style.map('Treeview', background=[('selected', '#0078d7')])  # Cor de seleção

    # ===== TELA DE LOGIN =====
    def _mostrar_tela_login(self):
        """Exibe a tela de login com campos para usuário e senha"""
        # Limpa a tela removendo todos os widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        # Título
        ttk.Label(frame, text="Controle de Estoque", font=('Arial', 16)).grid(row=0, column=0, pady=20, columnspan=2)

        # Campo de usuário
        ttk.Label(frame, text="Usuário:").grid(row=1, column=0, sticky='e')
        self.entry_user = ttk.Entry(frame)
        self.entry_user.grid(row=1, column=1, pady=5, padx=5)

        # Campo de senha (com caracteres ocultos)
        ttk.Label(frame, text="Senha:").grid(row=2, column=0, sticky='e')
        self.entry_pass = ttk.Entry(frame, show="*")
        self.entry_pass.grid(row=2, column=1, pady=5, padx=5)

        # Botão de login
        ttk.Button(frame, text="Login", command=self._fazer_login).grid(row=3, columnspan=2, pady=20)
    
    def _fazer_login(self):
        """Valida as credenciais e faz o login do usuário"""
        username = self.entry_user.get()
        password = self.entry_pass.get()

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Busca o usuário no banco de dados
            cursor.execute("SELECT password, perfil FROM usuarios WHERE username=?", (username,))
            resultado = cursor.fetchone()
            
            # Verifica a senha com bcrypt
            if resultado and bcrypt.checkpw(password.encode('utf-8'), resultado[0].encode('utf-8')):
                self.current_user = {
                    'username': username,
                    'perfil': resultado[1]  # 'Administrador' ou 'Comum'
                }
                self._mostrar_tela_principal()  # Vai para a tela principal
            else:
                messagebox.showerror("Erro", "Credenciais inválidas!")
        finally:
            conn.close()

    # ===== TELA PRINCIPAL =====
    def _mostrar_tela_principal(self):
        """Tela principal com menu e área de conteúdo dinâmico"""
        # Limpa a tela
        for widget in self.root.winfo_children():
            widget.destroy()

        # Barra superior com informações do usuário
        frame_superior = ttk.Frame(self.root)
        frame_superior.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame_superior, 
                 text=f"Usuário: {self.current_user['username']} ({self.current_user['perfil']})").pack(side=tk.LEFT)
        ttk.Button(frame_superior, text="Sair", command=self._mostrar_tela_login).pack(side=tk.RIGHT)

        # Menu principal
        frame_menu = ttk.Frame(self.root)
        frame_menu.pack(fill=tk.X, padx=10, pady=10)

        # Itens do menu disponíveis para todos
        botoes_menu = [
            ("📦 Produtos", self._mostrar_lista_produtos),
            ("🔃 Movimentação", self._mostrar_movimentacao),
            ("📊 Histórico", self._mostrar_historico)
        ]
        
        for texto, comando in botoes_menu:
            ttk.Button(frame_menu, text=texto, command=comando).pack(side=tk.LEFT, padx=5)

        # Menu de usuários só para administradores
        if self.current_user['perfil'] == "Administrador":
            ttk.Button(frame_menu, text="👥 Usuários", command=self._mostrar_cadastro_usuario).pack(side=tk.LEFT, padx=5)

        # Área de conteúdo dinâmico
        self.frame_conteudo = ttk.Frame(self.root)
        self.frame_conteudo.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Exibe a lista de produtos por padrão
        self._mostrar_lista_produtos()

    # ===== CADASTRO/EDIÇÃO DE PRODUTOS =====
    def _mostrar_formulario_produto(self, mode="cadastro", produto_id=None):
        """
        Exibe o formulário para cadastrar ou editar produtos
        Parâmetros:
        - mode: 'cadastro' ou 'edicao'
        - produto_id: ID do produto para edição (opcional)
        """
        # Limpa a área de conteúdo
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.frame_conteudo, padding=20)
        frame.pack(expand=True)

        # Título dinâmico
        titulo = "Editar Produto" if mode == "edicao" else "Cadastrar Novo Produto"
        ttk.Label(frame, text=titulo, font=('Arial', 14)).grid(row=0, columnspan=2, pady=10)

        # Variáveis para os campos do formulário
        campos = [
            ("Nome do Produto:", tk.StringVar()),
            ("Quantidade:", tk.StringVar()),
            ("Quantidade Mínima:", tk.StringVar())
        ]

        # Se for edição, carrega os dados do produto
        if mode == "edicao" and produto_id:
            conn = connect_db()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT nome, quantidade, quantidade_minima FROM produtos WHERE id=?", (produto_id,))
                resultado = cursor.fetchone()
                if resultado:
                    campos[0][1].set(resultado[0])  # Nome
                    campos[1][1].set(resultado[1])  # Quantidade
                    campos[2][1].set(resultado[2])  # Quantidade mínima
            finally:
                conn.close()

        # Cria os campos do formulário
        entries = []
        for row, (label, var) in enumerate(campos, start=1):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky='e', pady=5)
            entry = ttk.Entry(frame, textvariable=var)
            entry.grid(row=row, column=1, pady=5, padx=5, sticky='ew')
            entries.append(entry)

            # Validação para campos numéricos
            if "Quantidade" in label:
                entry.config(validate="key", 
                           validatecommand=(frame.register(lambda p: p.isdigit() or p == ""), '%P'))

        # Frame para os botões
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, columnspan=2, pady=20)

        if mode == "edicao":
            # Botões para edição
            ttk.Button(btn_frame, text="Salvar Alterações", 
                      command=lambda: self._salvar_produto(
                          produto_id,
                          campos[0][1].get(),
                          campos[1][1].get(),
                          campos[2][1].get()
                      )).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(btn_frame, text="Cancelar", 
                      command=self._mostrar_lista_produtos).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(btn_frame, text="Excluir Produto", 
                      command=lambda: self._confirmar_exclusao_produto(produto_id),
                      style="Red.TButton").pack(side=tk.RIGHT, padx=5)
        else:
            # Botão para cadastro
            ttk.Button(btn_frame, text="Cadastrar", 
                      command=lambda: self._cadastrar_produto(
                          campos[0][1].get(),
                          campos[1][1].get(),
                          campos[2][1].get()
                      )).pack(side=tk.LEFT)

    def _salvar_produto(self, produto_id, nome, quantidade, quantidade_minima):
        """Salva as alterações de um produto existente no banco de dados"""
        # Validação dos campos
        if not all([nome, quantidade, quantidade_minima]):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Atualiza o produto no banco
            cursor.execute(
                "UPDATE produtos SET nome=?, quantidade=?, quantidade_minima=? WHERE id=?",
                (nome, int(quantidade), int(quantidade_minima), produto_id)
            )
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            self._mostrar_lista_produtos()  # Atualiza a lista
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um produto com este nome!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def _confirmar_exclusao_produto(self, produto_id):
        """Exibe confirmação antes de excluir um produto"""
        resposta = messagebox.askyesno(
            "Confirmar Exclusão", 
            "Tem certeza que deseja excluir este produto?\nTodas as movimentações relacionadas também serão excluídas!",
            icon='warning'
        )
        
        if resposta:
            self._excluir_produto(produto_id)

    def _excluir_produto(self, produto_id):
        """Remove um produto e suas movimentações do banco de dados"""
        conn = connect_db()
        try:
            cursor = conn.cursor()
            
            # Primeiro exclui as movimentações relacionadas
            cursor.execute("DELETE FROM movimentacoes WHERE produto_id=?", (produto_id,))
            
            # Depois exclui o produto
            cursor.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            self._mostrar_lista_produtos()  # Atualiza a lista
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    # ===== LISTAGEM DE PRODUTOS =====
    def _mostrar_lista_produtos(self):
        """Exibe a lista de produtos em formato de tabela"""
        # Limpa a área de conteúdo
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.frame_conteudo)
        frame.pack(expand=True, fill=tk.BOTH)

        # Barra de ferramentas
        frame_toolbar = ttk.Frame(frame)
        frame_toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_toolbar, text="➕ Novo Produto", 
                  command=lambda: self._mostrar_formulario_produto("cadastro")).pack(side=tk.LEFT)
        
        ttk.Button(frame_toolbar, text="🔄 Atualizar", 
                  command=self._carregar_produtos).pack(side=tk.LEFT, padx=5)

        # Cria a tabela (Treeview)
        colunas = ("ID", "Nome", "Estoque", "Mínimo", "Status")
        self.tree_produtos = ttk.Treeview(
            frame, 
            columns=colunas, 
            show="headings",
            selectmode="browse"
        )
        
        # Configura as colunas
        for col in colunas:
            self.tree_produtos.heading(col, text=col)
            self.tree_produtos.column(col, width=80, anchor='center')
            
        # Ajustes de largura
        self.tree_produtos.column("Nome", width=250, anchor='w')
        self.tree_produtos.column("Status", width=150)
        
        self.tree_produtos.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Barra de rolagem
        scroll = ttk.Scrollbar(self.tree_produtos, orient="vertical", command=self.tree_produtos.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_produtos.configure(yscrollcommand=scroll.set)
        
        # Estilo para itens com estoque baixo
        self.tree_produtos.tag_configure('alerta', background='#ffeeee')
        
        # Evento de duplo clique para edição
        self.tree_produtos.bind("<Double-1>", self._editar_produto_selecionado)
        
        # Carrega os dados
        self._carregar_produtos()

    def _editar_produto_selecionado(self, event):
        """Abre o formulário de edição quando um produto é selecionado"""
        item = self.tree_produtos.selection()[0]
        produto_id = self.tree_produtos.item(item, 'values')[0]
        self._mostrar_formulario_produto("edicao", produto_id)

    def _carregar_produtos(self):
        """Carrega os produtos do banco de dados e exibe na tabela"""
        # Limpa a tabela
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
            
        conn = connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, quantidade, quantidade_minima FROM produtos ORDER BY nome")
            
            for produto in cursor.fetchall():
                id_, nome, qtd, min_qtd = produto
                # Define o status com base no estoque
                status = "OK" if qtd >= min_qtd else f"ESTOQUE BAIXO (mín: {min_qtd})"
                
                # Aplica estilo diferente para estoque baixo
                tags = ('alerta',) if qtd < min_qtd else ()
                self.tree_produtos.insert("", tk.END, values=(id_, nome, qtd, min_qtd, status), tags=tags)
        finally:
            conn.close()

    # ===== MOVIMENTAÇÃO DE ESTOQUE =====
    def _mostrar_movimentacao(self):
        """Exibe a interface para registrar movimentações de estoque"""
        # Limpa a área de conteúdo
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.frame_conteudo, padding=20)
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Movimentação de Estoque", font=('Arial', 14)).grid(row=0, columnspan=2, pady=10)

        # Seletor de produtos
        ttk.Label(frame, text="Selecione o Produto:").grid(row=1, column=0, sticky='e', pady=5)
        self.cb_produto = ttk.Combobox(frame, state="readonly")
        self.cb_produto.grid(row=1, column=1, pady=5, padx=5, sticky='ew')
        
        # Carrega os produtos no combobox
        conn = connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM produtos ORDER BY nome")
            produtos = [f"{p[0]} - {p[1]}" for p in cursor.fetchall()]
            self.cb_produto['values'] = produtos
            if produtos:
                self.cb_produto.current(0)  # Seleciona o primeiro item por padrão
        finally:
            conn.close()

        # Seleção do tipo de movimentação
        ttk.Label(frame, text="Tipo:").grid(row=2, column=0, sticky='e', pady=5)
        self.tipo_mov = tk.StringVar(value="saida")
        ttk.Radiobutton(frame, text="Saída", variable=self.tipo_mov, value="saida").grid(row=2, column=1, sticky='w')
        ttk.Radiobutton(frame, text="Entrada", variable=self.tipo_mov, value="entrada").grid(row=3, column=1, sticky='w')

        # Campo para quantidade
        ttk.Label(frame, text="Quantidade:").grid(row=4, column=0, sticky='e', pady=5)
        self.entry_qtd = ttk.Entry(frame, validate="key", 
                                 validatecommand=(frame.register(lambda p: p.isdigit() or p == ""), '%P'))
        self.entry_qtd.grid(row=4, column=1, pady=5, padx=5, sticky='ew')

        # Botão para confirmar a movimentação
        ttk.Button(frame, text="Confirmar", command=self._processar_movimentacao).grid(row=5, columnspan=2, pady=20)

        # Área para exibir informações do produto selecionado
        self.frame_info_produto = ttk.Frame(frame)
        self.frame_info_produto.grid(row=6, columnspan=2, sticky='ew', pady=10)
        
        # Atualiza as informações quando um produto é selecionado
        self.cb_produto.bind("<<ComboboxSelected>>", lambda e: self._atualizar_info_produto_movimentacao())

    def _atualizar_info_produto_movimentacao(self):
        """Atualiza as informações do produto selecionado na área de movimentação"""
        # Limpa as informações anteriores
        for widget in self.frame_info_produto.winfo_children():
            widget.destroy()

        produto = self.cb_produto.get()
        if not produto:
            return

        # Extrai o ID do produto do texto do combobox
        produto_id = int(produto.split(" - ")[0])
        
        conn = connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT nome, quantidade, quantidade_minima FROM produtos WHERE id=?", (produto_id,))
            resultado = cursor.fetchone()
            
            if resultado:
                nome, qtd, qtd_min = resultado
                
                # Exibe as informações do produto
                ttk.Label(self.frame_info_produto, text=f"Produto: {nome}").pack(anchor='w')
                ttk.Label(self.frame_info_produto, text=f"Estoque atual: {qtd}").pack(anchor='w')
                
                # Alerta se o estoque estiver abaixo do mínimo
                if qtd < qtd_min:
                    ttk.Label(self.frame_info_produto, 
                             text=f"ALERTA: Estoque abaixo do mínimo ({qtd_min})", 
                             style="Red.TLabel").pack(anchor='w')
                else:
                    ttk.Label(self.frame_info_produto, 
                             text=f"Estoque mínimo: {qtd_min}").pack(anchor='w')
        finally:
            conn.close()

    def _processar_movimentacao(self):
        """Processa a movimentação de estoque (entrada ou saída)"""
        produto = self.cb_produto.get()
        qtd_text = self.entry_qtd.get()
        tipo = self.tipo_mov.get()

        # Validações básicas
        if not produto or not qtd_text:
            messagebox.showerror("Erro", "Selecione um produto e informe a quantidade!")
            return

        try:
            produto_id = int(produto.split(" - ")[0])
            quantidade = int(qtd_text)
            
            # Valida a quantidade
            if quantidade <= 0:
                raise ValueError("A quantidade deve ser maior que zero!")

            conn = connect_db()
            cursor = conn.cursor()
            
            # Obtém o estoque atual
            cursor.execute("SELECT quantidade FROM produtos WHERE id=?", (produto_id,))
            estoque_atual = cursor.fetchone()[0]
            
            # Validação especial para saída
            if tipo == "saida" and quantidade > estoque_atual:
                raise ValueError(f"Estoque insuficiente! Disponível: {estoque_atual}")
            
            # Calcula a nova quantidade
            nova_quantidade = estoque_atual + quantidade if tipo == "entrada" else estoque_atual - quantidade
            
            # Atualiza o produto
            cursor.execute(
                "UPDATE produtos SET quantidade=? WHERE id=?", 
                (nova_quantidade, produto_id)
            )
            
            # Registra a movimentação no histórico
            cursor.execute(
                "INSERT INTO movimentacoes (produto_id, tipo, quantidade, data, usuario) VALUES (?, ?, ?, ?, ?)",
                (produto_id, tipo, quantidade, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                 self.current_user['username'])
            )
            
            conn.commit()
            messagebox.showinfo("Sucesso", f"Movimentação registrada: {tipo} de {quantidade} unidades")
            
            # Limpa e atualiza a interface
            self.entry_qtd.delete(0, tk.END)
            self._atualizar_info_produto_movimentacao()
            
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except sqlite3.Error as e:
            messagebox.showerror("Erro no Banco de Dados", f"Erro: {str(e)}")
            if conn:
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()

    # ===== CADASTRO DE USUÁRIOS =====
    def _mostrar_cadastro_usuario(self):
        """Exibe o formulário para cadastrar novos usuários (apenas para administradores)"""
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.frame_conteudo, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Cadastrar Novo Usuário", font=('Arial', 14)).grid(row=0, columnspan=2, pady=10)

        # Campos do formulário
        ttk.Label(frame, text="Nome de Usuário:").grid(row=1, column=0, sticky='e', pady=5)
        entry_user = ttk.Entry(frame)
        entry_user.grid(row=1, column=1, pady=5, padx=5, sticky='ew')

        ttk.Label(frame, text="Senha:").grid(row=2, column=0, sticky='e', pady=5)
        entry_pass = ttk.Entry(frame, show="*")
        entry_pass.grid(row=2, column=1, pady=5, padx=5, sticky='ew')

        ttk.Label(frame, text="Perfil:").grid(row=3, column=0, sticky='e', pady=5)
        combo_perfil = ttk.Combobox(frame, values=["Administrador", "Comum"], state="readonly")
        combo_perfil.grid(row=3, column=1, pady=5, padx=5, sticky='ew')
        combo_perfil.current(1)  # Define "Comum" como padrão

        # Botão de cadastro
        ttk.Button(frame, text="Cadastrar", command=lambda: self._cadastrar_usuario(
            entry_user.get(),
            entry_pass.get(),
            combo_perfil.get()
        )).grid(row=4, columnspan=2, pady=20)

    def _cadastrar_usuario(self, username, password, perfil):
        """Cadastra um novo usuário no sistema"""
        if not all([username, password, perfil]):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        conn = connect_db()
        try:
            # Criptografa a senha antes de armazenar
            senha_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (username, password, perfil) VALUES (?, ?, ?)",
                (username, senha_hash, perfil)
            )
            conn.commit()
            
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            # Limpa os campos
            for widget in self.frame_conteudo.winfo_children():
                if isinstance(widget, ttk.Entry):
                    widget.delete(0, tk.END)
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Nome de usuário já existe!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cadastrar: {str(e)}")
        finally:
            conn.close()

    # ===== HISTÓRICO DE MOVIMENTAÇÕES =====
    def _mostrar_historico(self):
        """Exibe o histórico completo de movimentações"""
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.frame_conteudo)
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Histórico de Movimentações", font=('Arial', 14)).pack(pady=10)

        # Cria a tabela
        colunas = ("ID", "Data", "Produto", "Tipo", "Quantidade", "Usuário")
        tree = ttk.Treeview(frame, columns=colunas, show="headings", height=20)
        
        # Configura as colunas
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')
            
        # Ajustes de largura
        tree.column("ID", width=50)
        tree.column("Data", width=150)
        tree.column("Produto", width=200, anchor='w')
        
        tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Barra de rolagem
        scroll = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scroll.set)
        
        # Carrega os dados
        conn = connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.id, m.data, p.nome, m.tipo, m.quantidade, m.usuario
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id
                ORDER BY m.data DESC
            ''')
            
            for mov in cursor.fetchall():
                tipo = "ENTRADA" if mov[3] == "entrada" else "SAÍDA"
                tree.insert("", tk.END, values=(mov[0], mov[1], mov[2], tipo, mov[4], mov[5]))
        finally:
            conn.close()

    # ===== FUNÇÕES AUXILIARES =====
    def _cadastrar_produto(self, nome, quantidade, quantidade_minima):
        """Cadastra um novo produto no sistema"""
        if not all([nome, quantidade, quantidade_minima]):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            # Insere o novo produto
            cursor.execute(
                "INSERT INTO produtos (nome, quantidade, quantidade_minima) VALUES (?, ?, ?)",
                (nome, int(quantidade), int(quantidade_minima))
            )
            
            # Registra a entrada inicial
            produto_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO movimentacoes (produto_id, tipo, quantidade, data, usuario) VALUES (?, ?, ?, ?, ?)",
                (produto_id, "entrada", int(quantidade), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                 self.current_user['username'])
            )
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            self._mostrar_lista_produtos()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um produto com este nome!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cadastrar: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

# ==============================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ==============================================

if __name__ == "__main__":
    app = ControleEstoqueApp()
    app.root.mainloop()
