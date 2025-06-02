# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
# Remova a importação de DateEntry se você a removeu completamente
# from tkcalendar import DateEntry 
from database import db_handler
from datetime import datetime

class AplicacaoAlunos:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Alunos - FacSenac")
        self.root.geometry("1200x750") # Pode precisar de mais espaço
        self.root.resizable(True, True)

        # --- Atributos para Ordenação ---
        self.coluna_ordenacao_atual = "nome" # Coluna padrão para ordenação
        self.direcao_ordenacao_atual_asc = True # True para ASC, False para DESC

        # Registra funções de validação para os campos de entrada
        self.vcmd_cpf = (self.root.register(self.validar_formato_cpf), '%d', '%P')
        self.vcmd_data = (self.root.register(self.validar_formato_data), '%d', '%P')
        self.vcmd_telefone = (self.root.register(self.validar_formato_telefone), '%d', '%P')

        self.criar_widgets_formulario()
        self.criar_widgets_busca_filtro() # NOVO: Frame para busca
        self.criar_widgets_botoes()
        self.criar_widgets_tabela()
        self.criar_barra_status() # NOVO: Barra de Status

        self.carregar_alunos_na_tabela() 

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
        # ... (lógica de validação do telefone como na resposta anterior) ...
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
        """Cria e organiza os campos de entrada de dados do aluno."""
        self.frame_formulario = ttk.LabelFrame(self.root, text="Dados do Aluno", padding=(15, 10))
        self.frame_formulario.pack(padx=10, pady=10, fill="x", side=tk.TOP) # Empacota no topo

        # ... (criação dos campos ID, Nome, Sobrenome, CPF, Data Nasc., Telefone, Email, Cidade, UF, Curso como antes) ...
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
        # Se você removeu DateEntry, este é o Entry normal:
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
        self.opcoes_curso = ['ADS', 'GTI', 'CD', 'IA', 'BI', 'SI'] # Mantido como antes
        self.combo_curso_var = tk.StringVar()
        self.combo_curso = ttk.Combobox(self.frame_formulario, textvariable=self.combo_curso_var, values=self.opcoes_curso, width=37, state="readonly")
        self.combo_curso.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        self.frame_formulario.columnconfigure(1, weight=1)
        self.frame_formulario.columnconfigure(3, weight=1)

    def criar_widgets_busca_filtro(self):
        """Cria os widgets para busca e filtro."""
        self.frame_busca = ttk.LabelFrame(self.root, text="Busca e Filtro", padding=(10,5))
        self.frame_busca.pack(padx=10, pady=(0,5), fill="x", side=tk.TOP)

        ttk.Label(self.frame_busca, text="Buscar por:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.search_field_options = ["Nome", "Sobrenome", "CPF", "Email", "Curso", "Cidade", "UF"]
        self.search_field_var = tk.StringVar(value=self.search_field_options[0]) # Padrão: Nome
        self.combo_search_field = ttk.Combobox(self.frame_busca, textvariable=self.search_field_var,
                                               values=self.search_field_options, state="readonly", width=15)
        self.combo_search_field.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame_busca, text="Termo:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.search_term_var = tk.StringVar()
        self.entry_search_term = ttk.Entry(self.frame_busca, textvariable=self.search_term_var, width=30)
        self.entry_search_term.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.entry_search_term.bind("<Return>", self.executar_busca) # Permite buscar com Enter

        self.btn_buscar = ttk.Button(self.frame_busca, text="Buscar", command=self.executar_busca)
        self.btn_buscar.grid(row=0, column=4, padx=5, pady=5)

        self.btn_limpar_busca = ttk.Button(self.frame_busca, text="Limpar Busca", command=self.limpar_busca)
        self.btn_limpar_busca.grid(row=0, column=5, padx=5, pady=5)
        
        self.frame_busca.columnconfigure(3, weight=1) # Faz o campo de termo expandir

    def criar_widgets_botoes(self):
        """Cria e organiza os botões de ação (CRUD)."""
        self.frame_botoes = ttk.Frame(self.root, padding=(10, 5))
        # Empacota abaixo do frame_formulario e frame_busca
        self.frame_botoes.pack(fill="x", side=tk.TOP, padx=10, pady=(0,5))

        # ... (botões como antes) ...
        self.btn_cadastrar = ttk.Button(self.frame_botoes, text="Cadastrar", command=self.cadastrar_aluno, style="Accent.TButton")
        self.btn_cadastrar.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_atualizar = ttk.Button(self.frame_botoes, text="Atualizar", command=self.atualizar_aluno_selecionado)
        self.btn_atualizar.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_deletar = ttk.Button(self.frame_botoes, text="Deletar", command=self.deletar_aluno_selecionado)
        self.btn_deletar.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar Campos", command=self.limpar_campos_formulario)
        self.btn_limpar.pack(side=tk.LEFT, padx=5, pady=5)


    def criar_widgets_tabela(self):
        """Cria e organiza a tabela (Treeview) para exibir os alunos."""
        self.frame_tabela = ttk.LabelFrame(self.root, text="Lista de Alunos", padding=(10,10))
        # Empacota abaixo dos outros frames, preenchendo o restante
        self.frame_tabela.pack(padx=10, pady=5, fill="both", expand=True, side=tk.TOP)

        # Nomes de coluna como no DB (ou como você quer que o backend os entenda para ordenação)
        # O texto do cabeçalho será formatado abaixo.
        self.colunas_db = { 
            "id": "ID", "nome": "Nome", "sobrenome": "Sobrenome", 
            "telefone": "Telefone", "email": "E-mail", "cpf": "CPF",
            # Para data_nascimento_formatada, a ordenação deve ser por 'data_nascimento'
            "data_nascimento_formatada": "Data Nasc.", 
            "cidade": "Cidade", "uf": "UF", "curso": "Curso"
        }
        # A ordem aqui define a ordem visual das colunas na Treeview
        self.colunas_visuais_ordenadas = ["id", "nome", "sobrenome", "cpf", "data_nascimento_formatada", "telefone", "email", "curso", "cidade", "uf"]


        self.tree_alunos = ttk.Treeview(self.frame_tabela, columns=self.colunas_visuais_ordenadas, show="headings", height=15)

        for col_key in self.colunas_visuais_ordenadas:
            display_text = self.colunas_db.get(col_key, col_key.capitalize())
            
            # Determina a coluna real do DB para ordenação
            db_sort_col = "data_nascimento" if col_key == "data_nascimento_formatada" else col_key
            
            self.tree_alunos.heading(col_key, text=display_text, 
                                     command=lambda c=db_sort_col: self.ordenar_coluna_tabela(c))
            
            # ... (configuração de largura das colunas como antes, usando col_key) ...
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

        # ... (Scrollbars como antes) ...
        scrollbar_y = ttk.Scrollbar(self.frame_tabela, orient=tk.VERTICAL, command=self.tree_alunos.yview)
        self.tree_alunos.configure(yscroll=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(self.frame_tabela, orient=tk.HORIZONTAL, command=self.tree_alunos.xview)
        self.tree_alunos.configure(xscroll=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_alunos.pack(fill="both", expand=True)
        self.tree_alunos.bind("<<TreeviewSelect>>", self.ao_selecionar_item_tabela)

    def criar_barra_status(self):
        """Cria a barra de status na parte inferior da janela."""
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)

    def atualizar_status(self, mensagem, sucesso=True, duracao_ms=5000):
        """Atualiza a mensagem na barra de status e a limpa após uma duração."""
        self.status_var.set(mensagem)
        # Define a cor do texto baseado no sucesso/erro (opcional)
        # self.status_bar.config(foreground="green" if sucesso else "red") 
        
        # Limpa a mensagem após a duração especificada
        if duracao_ms > 0:
            self.root.after(duracao_ms, lambda: self.status_var.set("Pronto"))
            # self.root.after(duracao_ms, lambda: self.status_bar.config(foreground="black")) # Restaura cor

    # --- Métodos para Busca e Ordenação ---
    def executar_busca(self, event=None): # event=None para ser chamado por botão ou Enter
        """Executa a busca com base nos campos preenchidos."""
        campo = self.search_field_var.get()
        termo = self.search_term_var.get().strip()
        
        if not termo: # Se o termo estiver vazio, carrega todos (ou mostra aviso)
            self.limpar_busca() # Limpa os campos e carrega todos
            # self.atualizar_status("Digite um termo para buscar.", sucesso=False)
            return
        
        self.carregar_alunos_na_tabela(search_field=campo, search_term=termo)
        self.atualizar_status(f"Buscando por '{termo}' em '{campo}'.")

    def limpar_busca(self):
        """Limpa os campos de busca e recarrega todos os alunos."""
        self.search_term_var.set("")
        # self.search_field_var.set(self.search_field_options[0]) # Opcional: resetar campo de busca
        self.carregar_alunos_na_tabela() # Carrega todos, sem ordenação específica (usa padrão)
        self.atualizar_status("Busca limpa. Exibindo todos os alunos.")
        self.entry_search_term.focus_set()

    def ordenar_coluna_tabela(self, coluna_clicada_db):
        """Ordena a tabela pela coluna clicada."""
        # Se clicou na mesma coluna, inverte a direção
        if coluna_clicada_db == self.coluna_ordenacao_atual:
            self.direcao_ordenacao_atual_asc = not self.direcao_ordenacao_atual_asc
        else: # Se clicou em nova coluna, ordena ascendente por padrão
            self.coluna_ordenacao_atual = coluna_clicada_db
            self.direcao_ordenacao_atual_asc = True
        
        direcao = 'ASC' if self.direcao_ordenacao_atual_asc else 'DESC'
        
        # Mantém os filtros de busca atuais ao reordenar
        campo_busca_atual = self.search_field_var.get()
        termo_busca_atual = self.search_term_var.get().strip()

        self.carregar_alunos_na_tabela(
            search_field=campo_busca_atual if termo_busca_atual else None,
            search_term=termo_busca_atual if termo_busca_atual else None,
            sort_by_column=self.coluna_ordenacao_atual,
            sort_direction=direcao
        )
        self.atualizar_status(f"Ordenado por {self.colunas_db.get(coluna_clicada_db, coluna_clicada_db)} ({direcao.lower()}).")


    # --- Métodos Principais (CRUD e Carregamento) ---
    def limpar_campos_formulario(self, focar_nome=True):
        # ... (como antes) ...
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
        # ... (como antes, mas a ordem dos valores[i] depende da ordem em self.colunas_visuais_ordenadas
        # e da query no db_handler.visualizar_alunos_db. É importante que a query retorne as colunas
        # na ordem que a Treeview espera, ou mapear corretamente aqui.)
        # A query atual retorna: id, nome, sobrenome, telefone, email, cpf, data_nasc_fmt, cidade, uf, curso
        item_selecionado = self.tree_alunos.focus()
        if not item_selecionado:
            return
        
        # Pega os valores da linha selecionada na Treeview
        # A ordem dos valores é a mesma definida em self.colunas_visuais_ordenadas
        # No entanto, a query do DB é quem realmente define a ordem dos dados retornados
        # A query SELECT é: id, nome, sobrenome, telefone, email, cpf, data_nascimento_formatada, cidade, uf, curso
        valores_linha = self.tree_alunos.item(item_selecionado, "values")

        if valores_linha and len(valores_linha) == len(self.colunas_visuais_ordenadas):
            # Mapeia os valores para as StringVars corretas
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


    # MODIFICADO para aceitar parâmetros de busca e ordenação
    def carregar_alunos_na_tabela(self, search_field=None, search_term=None, 
                                  sort_by_column=None, sort_direction='ASC'):
        """Busca alunos no BD (com filtros/ordenação) e exibe na Treeview."""
        for i in self.tree_alunos.get_children():
            self.tree_alunos.delete(i)

        # Usa a coluna de ordenação atual se nenhuma for passada (ex: na carga inicial)
        if sort_by_column is None:
            sort_by_column = self.coluna_ordenacao_atual
            sort_direction = 'ASC' if self.direcao_ordenacao_atual_asc else 'DESC'
            
        resultados, msg_status_db = db_handler.visualizar_alunos_db(
            search_field=search_field,
            search_term=search_term,
            sort_by_column=sort_by_column,
            sort_direction=sort_direction
        )
        
        if resultados is not None:
            for aluno in resultados:
                self.tree_alunos.insert("", tk.END, values=aluno)
            # Atualiza a mensagem da barra de status apenas se não for uma mensagem de erro
            if "Erro" not in msg_status_db :
                 self.atualizar_status(msg_status_db if msg_status_db else f"{len(resultados)} alunos carregados.")
            else: # Se for mensagem de erro do DB, mantém ela e não sobrescreve
                 self.atualizar_status(msg_status_db, sucesso=False)
        else:
            messagebox.showerror("Erro ao Carregar Alunos", msg_status_db)
            self.atualizar_status(msg_status_db if msg_status_db else "Falha ao carregar alunos.", sucesso=False)

    def validar_campos_obrigatorios(self):
        # ... (como antes) ...
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
        # ... (como antes) ...
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
        # ... (a lógica interna de pegar os valores e chamar db_handler como antes) ...
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
            messagebox.showinfo("Sucesso", msg) # Mantém o messagebox para confirmação explícita
            self.atualizar_status(msg, sucesso=True)
            self.limpar_campos_formulario(); self.carregar_alunos_na_tabela()
        else: 
            messagebox.showerror("Erro ao Cadastrar", msg)
            self.atualizar_status(msg, sucesso=False)

    def atualizar_aluno_selecionado(self):
        # ... (a lógica interna de pegar os valores e chamar db_handler como antes) ...
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
        # ... (a lógica interna como antes) ...
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