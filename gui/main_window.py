# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
# from tkcalendar import DateEntry # Removido se você reverteu
from database import db_handler
from datetime import datetime
import os # Para construir caminhos para os assets

class AplicacaoAlunos:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Alunos - FacSenac")
        self.root.geometry("1200x750")
        self.root.resizable(True, True)

        # --- Configuração de Temas ---
        self.is_dark_theme = False # Começa com tema claro
        self.light_theme = "arc"   # Seu tema claro padrão
        self.dark_theme = "equilux" # Um bom tema escuro do ttkthemes

        # --- Carregar Ícones ---
        self.carregar_icones()

        # --- Atributos para Ordenação ---
        self.coluna_ordenacao_atual = "nome"
        self.direcao_ordenacao_atual_asc = True

        # Registra funções de validação
        self.vcmd_cpf = (self.root.register(self.validar_formato_cpf), '%d', '%P')
        self.vcmd_data = (self.root.register(self.validar_formato_data), '%d', '%P')
        self.vcmd_telefone = (self.root.register(self.validar_formato_telefone), '%d', '%P')

        # Criação dos widgets da interface
        self.criar_widgets_barra_superior() # NOVO: Barra para botão de tema
        self.criar_widgets_formulario()
        self.criar_widgets_busca_filtro()
        self.criar_widgets_botoes() # Será modificado para incluir ícones
        self.criar_widgets_tabela()
        self.criar_barra_status()

        self.carregar_alunos_na_tabela()

    def carregar_icones(self):
        """Carrega os ícones da pasta assets."""
        # Constrói o caminho base para a pasta assets
        # __file__ é o caminho deste script (main_window.py)
        # os.path.dirname(__file__) é a pasta 'gui'
        base_path = os.path.join(os.path.dirname(__file__), "assets")
        
        icon_files = {
            "add": "add.png",
            "edit": "edit.png",
            "delete": "delete.png",
            "clear": "clear.png",
            "theme": "theme_icon.png" # Ícone para o botão de tema (opcional)
        }
        self.icons = {}

        for name, filename in icon_files.items():
            path = os.path.join(base_path, filename)
            try:
                self.icons[name] = tk.PhotoImage(file=path)
            except tk.TclError:
                print(f"Aviso: Ícone '{filename}' não encontrado em '{path}'. O botão ficará sem ícone.")
                self.icons[name] = None # Define como None se não encontrar

    def criar_widgets_barra_superior(self):
        """Cria uma barra superior para botões de ação globais como o de tema."""
        self.frame_barra_superior = ttk.Frame(self.root, padding=(5,5))
        self.frame_barra_superior.pack(fill=tk.X, side=tk.TOP, padx=10, pady=(5,0))

        self.btn_toggle_theme = ttk.Button(self.frame_barra_superior, 
                                           text="Alternar Tema", 
                                           image=self.icons.get("theme"), # Usa o ícone se carregado
                                           compound=tk.LEFT if self.icons.get("theme") else tk.NONE,
                                           command=self.alternar_tema)
        self.btn_toggle_theme.pack(side=tk.RIGHT) # Alinha à direita


    def alternar_tema(self):
        """Alterna entre o tema claro e escuro."""
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            try:
                self.root.set_theme(self.dark_theme)
                self.atualizar_status(f"Tema alterado para {self.dark_theme}.", duracao_ms=3000)
            except tk.TclError:
                messagebox.showwarning("Erro de Tema", f"Não foi possível carregar o tema escuro '{self.dark_theme}'. Verifique se ttkthemes está configurado corretamente.")
                self.is_dark_theme = False # Reverte se falhar
        else:
            try:
                self.root.set_theme(self.light_theme)
                self.atualizar_status(f"Tema alterado para {self.light_theme}.", duracao_ms=3000)
            except tk.TclError:
                 messagebox.showwarning("Erro de Tema", f"Não foi possível carregar o tema claro '{self.light_theme}'.")
        # Alguns widgets podem precisar ser redesenhados ou ter estilos reaplicados
        # A ThemedTk geralmente lida bem, mas para widgets Tk padrão, pode ser necessário mais.


    # --- Funções de Validação (CPF, Data, Telefone - como antes) ---
    def validar_formato_cpf(self, action_code, new_value_if_allowed):
        if action_code == '0': return True
        if len(new_value_if_allowed) > 14: return False
        for i, char in enumerate(new_value_if_allowed):
            if i in [3, 7]:
                if char != '.': return False
            elif i == 11:
                if char != '-': return False
            else:
                if not char.isdigit(): return False
        return True

    def validar_formato_data(self, action_code, new_value_if_allowed):
        if action_code == '0': return True
        if len(new_value_if_allowed) > 10: return False
        for i, char in enumerate(new_value_if_allowed):
            if i in [2, 5]:
                if char != '/': return False
            else:
                if not char.isdigit(): return False
        return True

    def validar_formato_telefone(self, action_code, new_value_if_allowed):
        if action_code == '0': return True
        max_len = 15
        if len(new_value_if_allowed) > max_len: return False
        is_valid = True
        for i, char in enumerate(new_value_if_allowed):
            if i == 0:
                if char != '(': is_valid = False; break
            elif i == 3:
                if char != ')': is_valid = False; break
            elif i == 4:
                if char != ' ': is_valid = False; break
            elif (max_len == 15 and i == 10) or (max_len == 14 and i == 9):
                if char != '-': is_valid = False; break
            elif i in [1, 2, 5, 6, 7, 8] or \
                 (max_len == 15 and i in [9, 11, 12, 13, 14]) or \
                 (max_len == 14 and i in [10, 11, 12, 13]):
                if not char.isdigit(): is_valid = False; break
            elif char not in "()- " and not char.isdigit():
                if not ( (i in [0,3,4,9,10] and char in "()- ") ):
                     if not char.isdigit():
                        is_valid = False; break
        if not is_valid:
            if len(new_value_if_allowed) <= 14:
                is_valid_14 = True
                for i, char_14 in enumerate(new_value_if_allowed):
                    if i == 0:
                        if char_14 != '(': is_valid_14 = False; break
                    elif i == 3:
                        if char_14 != ')': is_valid_14 = False; break
                    elif i == 4:
                        if char_14 != ' ': is_valid_14 = False; break
                    elif i == 9:
                        if char_14 != '-': is_valid_14 = False; break
                    elif i in [1, 2, 5, 6, 7, 8, 10, 11, 12, 13]:
                        if not char_14.isdigit(): is_valid_14 = False; break
                    elif char_14 not in "()- " and not char_14.isdigit():
                         if not ( (i in [0,3,4,9] and char_14 in "()- ") ):
                            if not char_14.isdigit():
                                is_valid_14 = False; break
                return is_valid_14
            return False
        return True

    def criar_widgets_formulario(self):
        self.frame_formulario = ttk.LabelFrame(self.root, text="Dados do Aluno", padding=(15, 10))
        self.frame_formulario.pack(padx=10, pady=(0,10), fill="x", side=tk.TOP) # pady ajustado

        # ... (campos do formulário como na última versão, sem alterações aqui) ...
        # Linha 0: ID
        ttk.Label(self.frame_formulario, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_id_var = tk.StringVar()
        self.entry_id = ttk.Entry(self.frame_formulario, textvariable=self.entry_id_var, width=10, state='readonly')
        self.entry_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Linha 1: Nome e Sobrenome
        ttk.Label(self.frame_formulario, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_nome_var = tk.StringVar()
        self.entry_nome = ttk.Entry(self.frame_formulario, textvariable=self.entry_nome_var, width=40)
        self.entry_nome.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.frame_formulario, text="Sobrenome:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_sobrenome_var = tk.StringVar()
        self.entry_sobrenome = ttk.Entry(self.frame_formulario, textvariable=self.entry_sobrenome_var, width=40)
        self.entry_sobrenome.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # Linha 2: CPF e Data de Nascimento
        ttk.Label(self.frame_formulario, text="CPF (###.###.###-##):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_cpf_var = tk.StringVar()
        self.entry_cpf = ttk.Entry(self.frame_formulario, textvariable=self.entry_cpf_var, width=20, validate="key", validatecommand=self.vcmd_cpf)
        self.entry_cpf.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.frame_formulario, text="Data Nasc. (DD/MM/AAAA):").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.entry_data_nasc_var = tk.StringVar()
        # Se você voltou para ttk.Entry para data:
        self.entry_data_nasc = ttk.Entry(self.frame_formulario, textvariable=self.entry_data_nasc_var, width=20, validate="key", validatecommand=self.vcmd_data)
        self.entry_data_nasc.grid(row=2, column=3, padx=5, pady=5, sticky="ew")


        # Linha 3: Telefone e Email
        ttk.Label(self.frame_formulario, text="Telefone ((##) #####-####):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_telefone_var = tk.StringVar()
        self.entry_telefone = ttk.Entry(self.frame_formulario, textvariable=self.entry_telefone_var, width=20, validate="key", validatecommand=self.vcmd_telefone)
        self.entry_telefone.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.frame_formulario, text="Email:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.entry_email_var = tk.StringVar()
        self.entry_email = ttk.Entry(self.frame_formulario, textvariable=self.entry_email_var, width=40)
        self.entry_email.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        # Linha 4: Cidade e UF
        ttk.Label(self.frame_formulario, text="Cidade:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_cidade_var = tk.StringVar(value="Brasília")
        self.entry_cidade = ttk.Entry(self.frame_formulario, textvariable=self.entry_cidade_var, width=30)
        self.entry_cidade.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.frame_formulario, text="UF:").grid(row=4, column=2, padx=5, pady=5, sticky="w")
        self.entry_uf_var = tk.StringVar(value="DF")
        self.entry_uf = ttk.Entry(self.frame_formulario, textvariable=self.entry_uf_var, width=5)
        self.entry_uf.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        # Linha 5: Curso
        ttk.Label(self.frame_formulario, text="Curso:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.opcoes_curso = ['ADS', 'GTI', 'CD', 'IA', 'BI', 'SI']
        self.combo_curso_var = tk.StringVar()
        self.combo_curso = ttk.Combobox(self.frame_formulario, textvariable=self.combo_curso_var, values=self.opcoes_curso, width=37, state="readonly")
        self.combo_curso.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        self.frame_formulario.columnconfigure(1, weight=1)
        self.frame_formulario.columnconfigure(3, weight=1)


    def criar_widgets_busca_filtro(self):
        self.frame_busca = ttk.LabelFrame(self.root, text="Busca e Filtro", padding=(10,5))
        self.frame_busca.pack(padx=10, pady=(0,5), fill="x", side=tk.TOP)
        # ... (widgets de busca como antes) ...
        ttk.Label(self.frame_busca, text="Buscar por:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_field_options = ["Nome", "Sobrenome", "CPF", "Email", "Curso", "Cidade", "UF"]
        self.search_field_var = tk.StringVar(value=self.search_field_options[0])
        self.combo_search_field = ttk.Combobox(self.frame_busca, textvariable=self.search_field_var,
                                               values=self.search_field_options, state="readonly", width=15)
        self.combo_search_field.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.frame_busca, text="Termo:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.search_term_var = tk.StringVar()
        self.entry_search_term = ttk.Entry(self.frame_busca, textvariable=self.search_term_var, width=30)
        self.entry_search_term.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.entry_search_term.bind("<Return>", self.executar_busca)
        self.btn_buscar = ttk.Button(self.frame_busca, text="Buscar", command=self.executar_busca)
        self.btn_buscar.grid(row=0, column=4, padx=5, pady=5)
        self.btn_limpar_busca = ttk.Button(self.frame_busca, text="Limpar Busca", command=self.limpar_busca)
        self.btn_limpar_busca.grid(row=0, column=5, padx=5, pady=5)
        self.frame_busca.columnconfigure(3, weight=1)


    def criar_widgets_botoes(self):
        """Cria e organiza os botões de ação (CRUD) com ícones."""
        self.frame_botoes = ttk.Frame(self.root, padding=(10, 5))
        self.frame_botoes.pack(fill="x", side=tk.TOP, padx=10, pady=(0,5))

        # Configura compound para que o texto apareça à direita do ícone
        compound_pos = tk.LEFT 

        self.btn_cadastrar = ttk.Button(self.frame_botoes, text="Cadastrar",
                                        image=self.icons.get("add"), compound=compound_pos, # Adiciona ícone
                                        command=self.cadastrar_aluno, style="Accent.TButton")
        self.btn_cadastrar.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_atualizar = ttk.Button(self.frame_botoes, text="Atualizar",
                                        image=self.icons.get("edit"), compound=compound_pos, # Adiciona ícone
                                        command=self.atualizar_aluno_selecionado)
        self.btn_atualizar.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_deletar = ttk.Button(self.frame_botoes, text="Deletar",
                                      image=self.icons.get("delete"), compound=compound_pos, # Adiciona ícone
                                      command=self.deletar_aluno_selecionado)
        self.btn_deletar.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar Campos",
                                     image=self.icons.get("clear"), compound=compound_pos, # Adiciona ícone
                                     command=self.limpar_campos_formulario)
        self.btn_limpar.pack(side=tk.LEFT, padx=5, pady=5)

    def criar_widgets_tabela(self):
        # ... (como antes, com a ordenação) ...
        self.frame_tabela = ttk.LabelFrame(self.root, text="Lista de Alunos", padding=(10,10))
        self.frame_tabela.pack(padx=10, pady=5, fill="both", expand=True, side=tk.TOP)
        self.colunas_db = { 
            "id": "ID", "nome": "Nome", "sobrenome": "Sobrenome", 
            "telefone": "Telefone", "email": "E-mail", "cpf": "CPF",
            "data_nascimento_formatada": "Data Nasc.", 
            "cidade": "Cidade", "uf": "UF", "curso": "Curso"
        }
        self.colunas_visuais_ordenadas = ["id", "nome", "sobrenome", "cpf", "data_nascimento_formatada", "telefone", "email", "curso", "cidade", "uf"]
        self.tree_alunos = ttk.Treeview(self.frame_tabela, columns=self.colunas_visuais_ordenadas, show="headings", height=15)
        for col_key in self.colunas_visuais_ordenadas:
            display_text = self.colunas_db.get(col_key, col_key.capitalize())
            db_sort_col = "data_nascimento" if col_key == "data_nascimento_formatada" else col_key
            self.tree_alunos.heading(col_key, text=display_text, command=lambda c=db_sort_col: self.ordenar_coluna_tabela(c))
            if col_key == "id": self.tree_alunos.column(col_key, width=40, minwidth=30, anchor=tk.CENTER)
            elif col_key == "nome": self.tree_alunos.column(col_key, width=150, minwidth=100)
            elif col_key == "sobrenome": self.tree_alunos.column(col_key, width=150, minwidth=100)
            elif col_key == "email": self.tree_alunos.column(col_key, width=180, minwidth=120)
            elif col_key == "telefone": self.tree_alunos.column(col_key, width=120, minwidth=100)
            elif col_key == "cpf": self.tree_alunos.column(col_key, width=110, minwidth=100, anchor=tk.CENTER)
            elif col_key == "data_nascimento_formatada": self.tree_alunos.column(col_key, width=100, minwidth=80, anchor=tk.CENTER)
            elif col_key == "cidade": self.tree_alunos.column(col_key, width=100, minwidth=80)
            elif col_key == "uf": self.tree_alunos.column(col_key, width=40, minwidth=30, anchor=tk.CENTER)
            elif col_key == "curso": self.tree_alunos.column(col_key, width=70, minwidth=60, anchor=tk.CENTER)
            else: self.tree_alunos.column(col_key, width=100)
        scrollbar_y = ttk.Scrollbar(self.frame_tabela, orient=tk.VERTICAL, command=self.tree_alunos.yview)
        self.tree_alunos.configure(yscroll=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(self.frame_tabela, orient=tk.HORIZONTAL, command=self.tree_alunos.xview)
        self.tree_alunos.configure(xscroll=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_alunos.pack(fill="both", expand=True)
        self.tree_alunos.bind("<<TreeviewSelect>>", self.ao_selecionar_item_tabela)


    def criar_barra_status(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)

    def atualizar_status(self, mensagem, sucesso=True, duracao_ms=5000):
        self.status_var.set(mensagem)
        if duracao_ms > 0:
            self.root.after(duracao_ms, lambda: self.status_var.set("Pronto"))

    # --- Métodos para Busca e Ordenação (como antes) ---
    def executar_busca(self, event=None):
        campo = self.search_field_var.get()
        termo = self.search_term_var.get().strip()
        if not termo:
            self.limpar_busca()
            return
        self.carregar_alunos_na_tabela(search_field=campo, search_term=termo)
        self.atualizar_status(f"Buscando por '{termo}' em '{campo}'.")

    def limpar_busca(self):
        self.search_term_var.set("")
        self.carregar_alunos_na_tabela()
        self.atualizar_status("Busca limpa. Exibindo todos os alunos.")
        self.entry_search_term.focus_set()

    def ordenar_coluna_tabela(self, coluna_clicada_db):
        if coluna_clicada_db == self.coluna_ordenacao_atual:
            self.direcao_ordenacao_atual_asc = not self.direcao_ordenacao_atual_asc
        else:
            self.coluna_ordenacao_atual = coluna_clicada_db
            self.direcao_ordenacao_atual_asc = True
        direcao = 'ASC' if self.direcao_ordenacao_atual_asc else 'DESC'
        campo_busca_atual = self.search_field_var.get()
        termo_busca_atual = self.search_term_var.get().strip()
        self.carregar_alunos_na_tabela(
            search_field=campo_busca_atual if termo_busca_atual else None,
            search_term=termo_busca_atual if termo_busca_atual else None,
            sort_by_column=self.coluna_ordenacao_atual,
            sort_direction=direcao
        )
        self.atualizar_status(f"Ordenado por {self.colunas_db.get(coluna_clicada_db, coluna_clicada_db)} ({direcao.lower()}).")

    # --- Métodos Principais (CRUD e Carregamento - como antes) ---
    def limpar_campos_formulario(self, focar_nome=True):
        self.entry_id_var.set("")
        self.entry_nome_var.set("")
        self.entry_sobrenome_var.set("")
        self.entry_cpf_var.set("")       
        self.entry_data_nasc_var.set("") 
        self.entry_telefone_var.set("")
        self.entry_email_var.set("")
        self.entry_cidade_var.set("Brasília")
        self.entry_uf_var.set("DF")
        self.combo_curso_var.set("")
        if focar_nome:
            self.entry_nome.focus_set()
        selecao = self.tree_alunos.selection()
        if selecao:
            self.tree_alunos.selection_remove(selecao)

    def ao_selecionar_item_tabela(self, event=None):
        item_selecionado = self.tree_alunos.focus()
        if not item_selecionado:
            return
        valores_linha = self.tree_alunos.item(item_selecionado, "values")
        if valores_linha and len(valores_linha) == len(self.colunas_visuais_ordenadas):
            self.entry_id_var.set(valores_linha[self.colunas_visuais_ordenadas.index("id")])
            self.entry_nome_var.set(valores_linha[self.colunas_visuais_ordenadas.index("nome")])
            self.entry_sobrenome_var.set(valores_linha[self.colunas_visuais_ordenadas.index("sobrenome")])
            self.entry_telefone_var.set(valores_linha[self.colunas_visuais_ordenadas.index("telefone")])
            self.entry_email_var.set(valores_linha[self.colunas_visuais_ordenadas.index("email")])
            self.entry_cpf_var.set(valores_linha[self.colunas_visuais_ordenadas.index("cpf")])
            self.entry_data_nasc_var.set(valores_linha[self.colunas_visuais_ordenadas.index("data_nascimento_formatada")])
            self.entry_cidade_var.set(valores_linha[self.colunas_visuais_ordenadas.index("cidade")])
            self.entry_uf_var.set(valores_linha[self.colunas_visuais_ordenadas.index("uf")])
            self.combo_curso_var.set(valores_linha[self.colunas_visuais_ordenadas.index("curso")])
        elif valores_linha:
            print(f"Aviso: Discrepância de valores ao selecionar. Recebido: {len(valores_linha)}, Esperado (colunas visuais): {len(self.colunas_visuais_ordenadas)}.")
            self.limpar_campos_formulario(focar_nome=False)

    def carregar_alunos_na_tabela(self, search_field=None, search_term=None, 
                                  sort_by_column=None, sort_direction='ASC'):
        for i in self.tree_alunos.get_children():
            self.tree_alunos.delete(i)
        if sort_by_column is None:
            sort_by_column = self.coluna_ordenacao_atual
            sort_direction = 'ASC' if self.direcao_ordenacao_atual_asc else 'DESC'
        resultados, msg_status_db = db_handler.visualizar_alunos_db(
            search_field=search_field, search_term=search_term,
            sort_by_column=sort_by_column, sort_direction=sort_direction
        )
        if resultados is not None:
            for aluno in resultados:
                self.tree_alunos.insert("", tk.END, values=aluno)
            if "Erro" not in msg_status_db :
                 self.atualizar_status(msg_status_db if msg_status_db else f"{len(resultados)} alunos carregados.")
            else:
                 self.atualizar_status(msg_status_db, sucesso=False)
        else:
            messagebox.showerror("Erro ao Carregar Alunos", msg_status_db)
            self.atualizar_status(msg_status_db if msg_status_db else "Falha ao carregar alunos.", sucesso=False)

    def validar_campos_obrigatorios(self):
        nome = self.entry_nome_var.get().strip()
        sobrenome = self.entry_sobrenome_var.get().strip()
        curso = self.combo_curso_var.get()
        cpf_str = self.entry_cpf_var.get().strip()
        data_nasc_str = self.entry_data_nasc_var.get().strip()
        telefone_str = self.entry_telefone_var.get().strip()
        if not nome or not sobrenome or not curso:
            messagebox.showwarning("Campos Obrigatórios", "Nome, Sobrenome e Curso são obrigatórios.")
            return False
        if cpf_str and not self.validar_formato_cpf('1', cpf_str):
            messagebox.showwarning("Formato Inválido", "Formato final do CPF inválido. Use ###.###.###-##.")
            self.entry_cpf.focus_set(); return False
        if data_nasc_str: 
            if not self.validar_formato_data('1', data_nasc_str):
                messagebox.showwarning("Formato Inválido", "Formato da Data de Nascimento inválido. Use DD/MM/AAAA.")
                self.entry_data_nasc.focus_set(); return False
            try: 
                datetime.strptime(data_nasc_str, '%d/%m/%Y')
            except ValueError:
                messagebox.showwarning("Data Inválida", "Data de Nascimento inválida (ex: dia ou mês não existe).")
                self.entry_data_nasc.focus_set(); return False
        if telefone_str and not self.validar_formato_telefone('1', telefone_str):
            if not (len(telefone_str) == 15 or len(telefone_str) == 14):
                messagebox.showwarning("Formato Inválido", "Formato final do Telefone inválido. Use (##) #####-#### ou (##) ####-####.")
                self.entry_telefone.focus_set(); return False
        return True

    def _formatar_data_para_db(self, data_str_ddmmyyyy):
        if not data_str_ddmmyyyy: return None
        try:
            data_obj = datetime.strptime(data_str_ddmmyyyy, '%d/%m/%Y')
            return data_obj.strftime('%Y-%m-%d')
        except ValueError:
            try:
                datetime.strptime(data_str_ddmmyyyy, '%Y-%m-%d')
                return data_str_ddmmyyyy
            except ValueError:
                print(f"Erro: Data '{data_str_ddmmyyyy}' não pôde ser formatada para o banco de dados.")
                return None

    def cadastrar_aluno(self):
        if not self.validar_campos_obrigatorios(): return
        cpf_val = self.entry_cpf_var.get().strip()
        data_nasc_db = self._formatar_data_para_db(self.entry_data_nasc_var.get().strip())
        dados_aluno = (
            self.entry_nome_var.get().strip(), self.entry_sobrenome_var.get().strip(),
            self.entry_telefone_var.get().strip() if self.entry_telefone_var.get().strip() else None,
            self.entry_email_var.get().strip() if self.entry_email_var.get().strip() else None,
            cpf_val if cpf_val else None, data_nasc_db,
            self.entry_cidade_var.get().strip() if self.entry_cidade_var.get().strip() else 'Brasília',
            self.entry_uf_var.get().strip().upper() if self.entry_uf_var.get().strip() else 'DF',
            self.combo_curso_var.get()
        )
        sucesso, msg = db_handler.cadastrar_aluno_db(dados_aluno)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.atualizar_status(msg, sucesso=True)
            self.limpar_campos_formulario(); self.carregar_alunos_na_tabela()
        else: 
            messagebox.showerror("Erro ao Cadastrar", msg)
            self.atualizar_status(msg, sucesso=False)

    def atualizar_aluno_selecionado(self):
        if not self.tree_alunos.focus(): messagebox.showwarning("Nenhuma Seleção", "Selecione um aluno na lista para atualizar."); return
        if not self.validar_campos_obrigatorios(): return
        id_aluno = self.entry_id_var.get()
        if not id_aluno: messagebox.showerror("Erro", "ID do aluno não encontrado para atualização."); return
        cpf_val = self.entry_cpf_var.get().strip()
        data_nasc_db = self._formatar_data_para_db(self.entry_data_nasc_var.get().strip())
        dados_aluno_atualizado = (
            self.entry_nome_var.get().strip(), self.entry_sobrenome_var.get().strip(),
            self.entry_telefone_var.get().strip() if self.entry_telefone_var.get().strip() else None,
            self.entry_email_var.get().strip() if self.entry_email_var.get().strip() else None,
            cpf_val if cpf_val else None, data_nasc_db,
            self.entry_cidade_var.get().strip() if self.entry_cidade_var.get().strip() else 'Brasília',
            self.entry_uf_var.get().strip().upper() if self.entry_uf_var.get().strip() else 'DF',
            self.combo_curso_var.get()
        )
        sucesso, msg = db_handler.atualizar_aluno_db(id_aluno, dados_aluno_atualizado)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.atualizar_status(msg, sucesso=True)
            self.limpar_campos_formulario(); self.carregar_alunos_na_tabela()
        else: 
            messagebox.showerror("Erro ao Atualizar", msg)
            self.atualizar_status(msg, sucesso=False)

    def deletar_aluno_selecionado(self):
        if not self.tree_alunos.focus(): messagebox.showwarning("Nenhuma Seleção", "Selecione um aluno na lista para deletar."); return
        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir este aluno? Esta ação não pode ser desfeita."): return
        id_aluno = self.entry_id_var.get()
        if not id_aluno: messagebox.showerror("Erro", "ID do aluno não encontrado para deleção."); return
        sucesso, msg = db_handler.deletar_aluno_db(id_aluno)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.atualizar_status(msg, sucesso=True)
            self.limpar_campos_formulario(); self.carregar_alunos_na_tabela()
        else: 
            messagebox.showerror("Erro ao Deletar", msg)
            self.atualizar_status(msg, sucesso=False)

# --- Fim da classe AplicacaoAlunos ---