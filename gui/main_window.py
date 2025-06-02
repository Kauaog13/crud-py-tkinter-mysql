# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
# from tkcalendar import DateEntry # Se você removeu
from database import db_handler
from utils import validators 
from datetime import datetime
import os 
import logging

logger = logging.getLogger(__name__)

class AplicacaoAlunos:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Alunos - FacSenac")
        self.root.geometry("1200x750") 
        self.root.resizable(True, True)
        logger.info("Janela principal AplicacaoAlunos inicializada.")

        self.is_dark_theme = False 
        self.light_theme = "arc"   
        self.dark_theme = "equilux" 

        # self.configurar_estilos_botoes() # Não é mais necessário para hover específico
        self.carregar_icones()

        self.coluna_ordenacao_atual = "nome" 
        self.direcao_ordenacao_atual_asc = True 

        self.vcmd_cpf = (self.root.register(self.validar_formato_cpf), '%d', '%P')
        self.vcmd_data = (self.root.register(self.validar_formato_data), '%d', '%P')
        self.vcmd_telefone = (self.root.register(self.validar_formato_telefone), '%d', '%P')

        self.criar_widgets_barra_superior()
        self.criar_widgets_formulario()
        self.criar_widgets_busca_filtro()
        self.criar_widgets_botoes() 
        self.criar_widgets_tabela()
        self.criar_barra_status()

        self.carregar_alunos_na_tabela()

    def configurar_estilos_botoes(self):
        """
        Define estilos personalizados para os botões.
        Removidas as configurações de hover para Cadastrar, Atualizar, Deletar.
        Este método pode ser usado para outros estilos globais de botões se necessário.
        """
        style = ttk.Style()
        # Se você tiver outras configurações de estilo base para TButton que queira manter,
        # elas podem ficar aqui. Por exemplo:
        # style.configure("TButton", font=('Helvetica', 10), padding=5)
        
        # As chamadas style.map() para "Cadastrar.TButton", "Atualizar.TButton", 
        # e "Deletar.TButton" que definiam o hover foram removidas.
        logger.debug("Estilos de hover personalizados para botões CRUD foram removidos.")


    def carregar_icones(self):
        logger.debug("Carregando ícones...")
        base_path = os.path.join(os.path.dirname(__file__), "assets")
        icon_files = {
            "add": "add.png", "edit": "edit.png", "delete": "delete.png",
            "clear": "clear.png", "theme": "theme_icon.png"
        }
        self.icons = {}
        for name, filename in icon_files.items():
            path = os.path.join(base_path, filename)
            try:
                self.icons[name] = tk.PhotoImage(file=path)
                logger.debug(f"Ícone '{filename}' carregado de '{path}'.")
            except tk.TclError:
                logger.warning(f"Ícone '{filename}' não encontrado ou erro ao carregar de '{path}'.")
                self.icons[name] = None

    def criar_widgets_barra_superior(self):
        logger.debug("Criando widgets da barra superior.")
        self.frame_barra_superior = ttk.Frame(self.root, padding=(5,5))
        self.frame_barra_superior.pack(fill=tk.X, side=tk.TOP, padx=10, pady=(5,0))
        self.btn_toggle_theme = ttk.Button(self.frame_barra_superior, 
                                           text="Alternar Tema", 
                                           image=self.icons.get("theme"),
                                           compound=tk.LEFT if self.icons.get("theme") else tk.NONE,
                                           command=self.alternar_tema)
        self.btn_toggle_theme.pack(side=tk.RIGHT)

    def alternar_tema(self):
        self.is_dark_theme = not self.is_dark_theme
        new_theme = self.dark_theme if self.is_dark_theme else self.light_theme
        logger.info(f"Tentando alterar tema para: {new_theme}")
        try:
            self.root.set_theme(new_theme)
            self.atualizar_status(f"Tema alterado para {new_theme}.", duracao_ms=3000)
            logger.info(f"Tema alterado com sucesso para {new_theme}.")
        except tk.TclError as e:
            logger.error(f"Falha ao carregar tema '{new_theme}': {e}")
            messagebox.showwarning("Erro de Tema", f"Não foi possível carregar o tema '{new_theme}'.")
            if new_theme == self.dark_theme: self.is_dark_theme = False

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
        logger.debug("Criando widgets do formulário.")
        self.frame_formulario = ttk.LabelFrame(self.root, text="Dados do Aluno", padding=(15, 10))
        self.frame_formulario.pack(padx=10, pady=(0,10), fill="x", side=tk.TOP)
        
        ttk.Label(self.frame_formulario, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_id_var = tk.StringVar()
        self.entry_id = ttk.Entry(self.frame_formulario, textvariable=self.entry_id_var, width=10, state='readonly')
        self.entry_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame_formulario, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_nome_var = tk.StringVar()
        self.entry_nome = ttk.Entry(self.frame_formulario, textvariable=self.entry_nome_var, width=40)
        self.entry_nome.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.frame_formulario, text="Sobrenome:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_sobrenome_var = tk.StringVar()
        self.entry_sobrenome = ttk.Entry(self.frame_formulario, textvariable=self.entry_sobrenome_var, width=40)
        self.entry_sobrenome.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame_formulario, text="CPF (###.###.###-##):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_cpf_var = tk.StringVar()
        self.entry_cpf = ttk.Entry(self.frame_formulario, textvariable=self.entry_cpf_var, width=20, validate="key", validatecommand=self.vcmd_cpf)
        self.entry_cpf.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(self.frame_formulario, text="Data Nasc. (DD/MM/AAAA):").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.entry_data_nasc_var = tk.StringVar()
        self.entry_data_nasc = ttk.Entry(self.frame_formulario, textvariable=self.entry_data_nasc_var, width=20, validate="key", validatecommand=self.vcmd_data)
        self.entry_data_nasc.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame_formulario, text="Telefone ((##) #####-####):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_telefone_var = tk.StringVar()
        self.entry_telefone = ttk.Entry(self.frame_formulario, textvariable=self.entry_telefone_var, width=20, validate="key", validatecommand=self.vcmd_telefone)
        self.entry_telefone.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.frame_formulario, text="Email:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.entry_email_var = tk.StringVar()
        self.entry_email = ttk.Entry(self.frame_formulario, textvariable=self.entry_email_var, width=40)
        self.entry_email.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame_formulario, text="Cidade:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_cidade_var = tk.StringVar(value="Brasília")
        self.entry_cidade = ttk.Entry(self.frame_formulario, textvariable=self.entry_cidade_var, width=30)
        self.entry_cidade.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.frame_formulario, text="UF:").grid(row=4, column=2, padx=5, pady=5, sticky="w")
        self.entry_uf_var = tk.StringVar(value="DF")
        self.entry_uf = ttk.Entry(self.frame_formulario, textvariable=self.entry_uf_var, width=5)
        self.entry_uf.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(self.frame_formulario, text="Curso:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.opcoes_curso = ['ADS', 'GTI', 'CD', 'IA', 'BI', 'SI']
        self.combo_curso_var = tk.StringVar()
        self.combo_curso = ttk.Combobox(self.frame_formulario, textvariable=self.combo_curso_var, values=self.opcoes_curso, width=37, state="readonly")
        self.combo_curso.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        self.frame_formulario.columnconfigure(1, weight=1)
        self.frame_formulario.columnconfigure(3, weight=1)

    def criar_widgets_busca_filtro(self):
        logger.debug("Criando widgets de busca/filtro.")
        self.frame_busca = ttk.LabelFrame(self.root, text="Busca e Filtro", padding=(10,5))
        self.frame_busca.pack(padx=10, pady=(0,5), fill="x", side=tk.TOP)
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
        """Cria os botões CRUD, agora usando o estilo padrão TButton (sem hover customizado)."""
        logger.debug("Criando widgets de botões CRUD (sem hover customizado).")
        self.frame_botoes = ttk.Frame(self.root, padding=(10, 5))
        self.frame_botoes.pack(fill="x", side=tk.TOP, padx=10, pady=(0,5))
        compound_pos = tk.LEFT 

        self.btn_cadastrar = ttk.Button(self.frame_botoes, text="Cadastrar",
                                        image=self.icons.get("add"), compound=compound_pos,
                                        command=self.cadastrar_aluno, 
                                        style="TButton") # Revertido para estilo padrão
        self.btn_cadastrar.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_atualizar = ttk.Button(self.frame_botoes, text="Atualizar",
                                        image=self.icons.get("edit"), compound=compound_pos,
                                        command=self.atualizar_aluno_selecionado,
                                        style="TButton") # Revertido para estilo padrão
        self.btn_atualizar.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_deletar = ttk.Button(self.frame_botoes, text="Deletar",
                                      image=self.icons.get("delete"), compound=compound_pos,
                                      command=self.deletar_aluno_selecionado,
                                      style="TButton") # Revertido para estilo padrão
        self.btn_deletar.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar Campos",
                                     image=self.icons.get("clear"), compound=compound_pos,
                                     command=self.limpar_campos_formulario,
                                     style="TButton") # Já era padrão
        self.btn_limpar.pack(side=tk.LEFT, padx=5, pady=5)

    def criar_widgets_tabela(self):
        logger.debug("Criando widget da tabela (Treeview).")
        self.frame_tabela = ttk.LabelFrame(self.root, text="Lista de Alunos", padding=(10,10))
        self.frame_tabela.pack(padx=10, pady=5, fill="both", expand=True, side=tk.TOP)
        self.map_coluna_cabecalho = { 
            "id": "ID", "nome": "Nome", "sobrenome": "Sobrenome", 
            "telefone": "Telefone", "email": "E-mail", "cpf": "CPF",
            "data_nascimento_formatada": "Data Nasc.", 
            "cidade": "Cidade", "uf": "UF", "curso": "Curso"
        }
        self.colunas_visuais_treeview = ["id", "nome", "sobrenome", "cpf", "data_nascimento_formatada", "telefone", "email", "curso", "cidade", "uf"]
        self.tree_alunos = ttk.Treeview(self.frame_tabela, columns=self.colunas_visuais_treeview, show="headings", height=15)
        for col_key in self.colunas_visuais_treeview:
            display_text = self.map_coluna_cabecalho.get(col_key, col_key.capitalize())
            db_sort_col = "data_nascimento" if col_key == "data_nascimento_formatada" else col_key
            self.tree_alunos.heading(col_key, text=display_text, command=lambda c=db_sort_col: self.ordenar_coluna_tabela(c))
            if col_key == "id": self.tree_alunos.column(col_key, width=40, anchor=tk.CENTER)
            elif col_key == "nome": self.tree_alunos.column(col_key, width=150)
            elif col_key == "sobrenome": self.tree_alunos.column(col_key, width=150)
            elif col_key == "email": self.tree_alunos.column(col_key, width=180)
            elif col_key == "telefone": self.tree_alunos.column(col_key, width=120)
            elif col_key == "cpf": self.tree_alunos.column(col_key, width=110, anchor=tk.CENTER)
            elif col_key == "data_nascimento_formatada": self.tree_alunos.column(col_key, width=100, anchor=tk.CENTER)
            elif col_key == "cidade": self.tree_alunos.column(col_key, width=100)
            elif col_key == "uf": self.tree_alunos.column(col_key, width=40, anchor=tk.CENTER)
            elif col_key == "curso": self.tree_alunos.column(col_key, width=70, anchor=tk.CENTER)
            else: self.tree_alunos.column(col_key, width=100)
        scrollbar_y = ttk.Scrollbar(self.frame_tabela, orient=tk.VERTICAL, command=self.tree_alunos.yview)
        self.tree_alunos.configure(yscroll=scrollbar_y.set); scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x = ttk.Scrollbar(self.frame_tabela, orient=tk.HORIZONTAL, command=self.tree_alunos.xview)
        self.tree_alunos.configure(xscroll=scrollbar_x.set); scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_alunos.pack(fill="both", expand=True)
        self.tree_alunos.bind("<<TreeviewSelect>>", self.ao_selecionar_item_tabela)

    def criar_barra_status(self):
        logger.debug("Criando barra de status.")
        self.status_var = tk.StringVar(); self.status_var.set("Pronto")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)

    def atualizar_status(self, mensagem, sucesso=True, duracao_ms=5000):
        logger.info(f"Atualizando status: '{mensagem}' (Sucesso: {sucesso})")
        self.status_var.set(mensagem)
        if duracao_ms > 0:
            self.root.after(duracao_ms, lambda: self.status_var.set("Pronto"))

    def executar_busca(self, event=None):
        campo = self.search_field_var.get()
        termo = self.search_term_var.get().strip()
        logger.info(f"Executando busca: Campo='{campo}', Termo='{termo}'")
        if not termo: self.limpar_busca(); return
        self.carregar_alunos_na_tabela(search_field=campo, search_term=termo,
                                       sort_by_column=self.coluna_ordenacao_atual,
                                       sort_direction='ASC' if self.direcao_ordenacao_atual_asc else 'DESC')
        self.atualizar_status(f"Buscando por '{termo}' em '{campo}'.")

    def limpar_busca(self):
        logger.info("Limpando busca.")
        self.search_term_var.set("")
        self.carregar_alunos_na_tabela(sort_by_column=self.coluna_ordenacao_atual,
                                       sort_direction='ASC' if self.direcao_ordenacao_atual_asc else 'DESC')
        self.atualizar_status("Busca limpa. Exibindo todos os alunos.")
        self.entry_search_term.focus_set()

    def ordenar_coluna_tabela(self, coluna_clicada_db):
        if coluna_clicada_db == self.coluna_ordenacao_atual:
            self.direcao_ordenacao_atual_asc = not self.direcao_ordenacao_atual_asc
        else:
            self.coluna_ordenacao_atual = coluna_clicada_db
            self.direcao_ordenacao_atual_asc = True
        direcao = 'ASC' if self.direcao_ordenacao_atual_asc else 'DESC'
        logger.info(f"Ordenando tabela por '{coluna_clicada_db}' na direção '{direcao}'.")
        campo_busca_atual = self.search_field_var.get()
        termo_busca_atual = self.search_term_var.get().strip()
        self.carregar_alunos_na_tabela(
            search_field=campo_busca_atual if termo_busca_atual else None,
            search_term=termo_busca_atual if termo_busca_atual else None,
            sort_by_column=self.coluna_ordenacao_atual,
            sort_direction=direcao )
        nome_exibicao_coluna = coluna_clicada_db.capitalize()
        for key_visual, texto_cabecalho in self.map_coluna_cabecalho.items():
            db_col = "data_nascimento" if key_visual == "data_nascimento_formatada" else key_visual
            if coluna_clicada_db == db_col:
                nome_exibicao_coluna = texto_cabecalho; break
        self.atualizar_status(f"Ordenado por {nome_exibicao_coluna} ({direcao.lower()}).")

    def limpar_campos_formulario(self, focar_nome=True):
        logger.debug("Limpando campos do formulário.")
        self.entry_id_var.set(""); self.entry_nome_var.set(""); self.entry_sobrenome_var.set("")
        self.entry_cpf_var.set(""); self.entry_data_nasc_var.set(""); self.entry_telefone_var.set("")
        self.entry_email_var.set(""); self.entry_cidade_var.set("Brasília"); self.entry_uf_var.set("DF")
        self.combo_curso_var.set("")
        if focar_nome: self.entry_nome.focus_set()
        selecao = self.tree_alunos.selection()
        if selecao: self.tree_alunos.selection_remove(selecao)

    def ao_selecionar_item_tabela(self, event=None):
        item_selecionado = self.tree_alunos.focus()
        if not item_selecionado: return
        valores_linha = self.tree_alunos.item(item_selecionado, "values")
        if valores_linha and len(valores_linha) == 10:
            logger.debug(f"Item selecionado na tabela: ID={valores_linha[0]}, Nome='{valores_linha[1]}'")
            self.entry_id_var.set(str(valores_linha[0]))
            self.entry_nome_var.set(str(valores_linha[1]))
            self.entry_sobrenome_var.set(str(valores_linha[2]))
            self.entry_telefone_var.set(str(valores_linha[3]))
            self.entry_email_var.set(str(valores_linha[4]))
            self.entry_cpf_var.set(str(valores_linha[5]))
            self.entry_data_nasc_var.set(str(valores_linha[6]))
            self.entry_cidade_var.set(str(valores_linha[7]))
            self.entry_uf_var.set(str(valores_linha[8]))
            self.combo_curso_var.set(str(valores_linha[9]))
        elif valores_linha:
            logger.warning(f"Discrepância de valores ao selecionar. Recebido: {len(valores_linha)}, Esperado: 10. Valores: {valores_linha}")
            self.limpar_campos_formulario(focar_nome=False)

    def carregar_alunos_na_tabela(self, search_field=None, search_term=None, 
                                  sort_by_column=None, sort_direction='ASC'):
        logger.info(f"Carregando alunos: busca='{search_field}':'{search_term}', ordenar='{sort_by_column}':'{sort_direction}'")
        for i in self.tree_alunos.get_children(): self.tree_alunos.delete(i)
        if sort_by_column is None:
            sort_by_column = self.coluna_ordenacao_atual
            sort_direction = 'ASC' if self.direcao_ordenacao_atual_asc else 'DESC'
        resultados, msg_status_db = db_handler.visualizar_alunos_db(
            search_field=search_field, search_term=search_term,
            sort_by_column=sort_by_column, sort_direction=sort_direction)
        if resultados is not None:
            logger.debug(f"{len(resultados)} alunos retornados do DB para exibição.")
            for aluno in resultados: self.tree_alunos.insert("", tk.END, values=aluno)
            if "Erro" not in msg_status_db :
                 self.atualizar_status(msg_status_db if msg_status_db else f"{len(resultados)} alunos carregados.")
            else: self.atualizar_status(msg_status_db, sucesso=False)
        else:
            logger.error(f"Falha ao carregar alunos do DB: {msg_status_db}")
            messagebox.showerror("Erro ao Carregar Alunos", msg_status_db)
            self.atualizar_status(msg_status_db if msg_status_db else "Falha ao carregar alunos.", sucesso=False)

    def validar_campos_obrigatorios(self):
        logger.debug("Iniciando validação de campos obrigatórios e formatos.")
        nome = self.entry_nome_var.get().strip(); sobrenome = self.entry_sobrenome_var.get().strip()
        curso = self.combo_curso_var.get(); cpf_str = self.entry_cpf_var.get().strip()
        data_nasc_str_gui = self.entry_data_nasc_var.get().strip()
        telefone_str = self.entry_telefone_var.get().strip(); email_str = self.entry_email_var.get().strip()

        if not nome or not sobrenome or not curso:
            logger.warning("Validação falhou: Nome, Sobrenome ou Curso não preenchidos.")
            messagebox.showwarning("Campos Obrigatórios", "Nome, Sobrenome e Curso são obrigatórios."); return False
        if cpf_str:
            valido_cpf, msg_cpf = validators.validar_cpf_completo(cpf_str)
            if not valido_cpf:
                logger.warning(f"Validação de CPF falhou (GUI): {msg_cpf} para CPF: {cpf_str}")
                messagebox.showwarning("Validação Falhou", msg_cpf); self.entry_cpf.focus_set(); return False
        if email_str:
            valido_email, msg_email = validators.validar_email_formato(email_str)
            if not valido_email:
                logger.warning(f"Validação de Email falhou (GUI): {msg_email} para Email: {email_str}")
                messagebox.showwarning("Validação Falhou", msg_email); self.entry_email.focus_set(); return False
        if telefone_str:
            valido_tel, msg_tel = validators.validar_telefone_formato(telefone_str)
            if not valido_tel:
                logger.warning(f"Validação de Telefone falhou (GUI): {msg_tel} para Tel: {telefone_str}")
                messagebox.showwarning("Validação Falhou", msg_tel); self.entry_telefone.focus_set(); return False
        if data_nasc_str_gui:
            if not self.validar_formato_data('1', data_nasc_str_gui):
                logger.warning(f"Validação de formato de Data Nasc. falhou (GUI): {data_nasc_str_gui}")
                messagebox.showwarning("Formato Inválido", "Data Nasc.: DD/MM/AAAA."); self.entry_data_nasc.focus_set(); return False
            try: datetime.strptime(data_nasc_str_gui, '%d/%m/%Y')
            except ValueError:
                logger.warning(f"Validação semântica de Data Nasc. falhou (GUI): {data_nasc_str_gui}")
                messagebox.showwarning("Data Inválida", "Data Nasc.: dia ou mês não existe."); self.entry_data_nasc.focus_set(); return False
            data_nasc_para_backend = self._formatar_data_para_db(data_nasc_str_gui)
            logger.debug(f"[GUI Validar] Data GUI: {data_nasc_str_gui}, Formatada para Idade Check: {data_nasc_para_backend}")
            if data_nasc_para_backend:
                valido_idade, msg_idade = validators.validar_data_nascimento_e_idade(data_nasc_para_backend)
                if not valido_idade:
                    logger.warning(f"Validação de Idade falhou (GUI): {msg_idade} para Data: {data_nasc_para_backend}")
                    messagebox.showwarning("Validação Falhou", msg_idade); self.entry_data_nasc.focus_set(); return False
            else:
                 logger.error(f"Erro interno na GUI: _formatar_data_para_db retornou None para data não vazia '{data_nasc_str_gui}'")
                 messagebox.showwarning("Erro Interno", "Não foi possível formatar a data para validação de idade."); return False
        logger.debug("Validação de campos na GUI passou.")
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
                logger.warning(f"Data '{data_str_ddmmyyyy}' não pôde ser formatada para o banco de dados (formatos DD/MM/YYYY ou YYYY-MM-DD).")
                return None

    def cadastrar_aluno(self):
        logger.info("Botão 'Cadastrar Aluno' clicado.")
        if not self.validar_campos_obrigatorios(): 
            logger.warning("Cadastro abortado devido a falha na validação da GUI.")
            return
        dados_aluno = (
            self.entry_nome_var.get().strip(), self.entry_sobrenome_var.get().strip(),
            self.entry_telefone_var.get().strip() or None, self.entry_email_var.get().strip() or None,
            self.entry_cpf_var.get().strip() or None,
            self._formatar_data_para_db(self.entry_data_nasc_var.get().strip()),
            self.entry_cidade_var.get().strip() or 'Brasília',
            self.entry_uf_var.get().strip().upper() or 'DF', self.combo_curso_var.get()
        )
        logger.debug(f"Dados para cadastro: {dados_aluno}")
        sucesso, msg = db_handler.cadastrar_aluno_db(dados_aluno)
        if sucesso:
            logger.info(f"Aluno cadastrado com sucesso: {msg}")
            messagebox.showinfo("Sucesso", msg); self.atualizar_status(msg, sucesso=True)
            self.limpar_campos_formulario(); self.carregar_alunos_na_tabela()
        else: 
            logger.error(f"Falha ao cadastrar aluno (retorno do DB): {msg}")
            messagebox.showerror("Erro ao Cadastrar", msg); self.atualizar_status(msg, sucesso=False)

    def atualizar_aluno_selecionado(self):
        logger.info("Botão 'Atualizar Aluno' clicado.")
        if not self.tree_alunos.focus(): messagebox.showwarning("Nenhuma Seleção", "Selecione um aluno."); return
        if not self.validar_campos_obrigatorios(): 
            logger.warning("Atualização abortada devido a falha na validação da GUI.")
            return
        id_aluno = self.entry_id_var.get()
        if not id_aluno: logger.error("Tentativa de atualização sem ID de aluno."); messagebox.showerror("Erro", "ID do aluno não encontrado."); return
        dados_aluno_atualizado = (
            self.entry_nome_var.get().strip(), self.entry_sobrenome_var.get().strip(),
            self.entry_telefone_var.get().strip() or None, self.entry_email_var.get().strip() or None,
            self.entry_cpf_var.get().strip() or None,
            self._formatar_data_para_db(self.entry_data_nasc_var.get().strip()),
            self.entry_cidade_var.get().strip() or 'Brasília',
            self.entry_uf_var.get().strip().upper() or 'DF', self.combo_curso_var.get()
        )
        logger.debug(f"Dados para atualização (ID: {id_aluno}): {dados_aluno_atualizado}")
        sucesso, msg = db_handler.atualizar_aluno_db(id_aluno, dados_aluno_atualizado)
        if sucesso:
            logger.info(f"Aluno ID {id_aluno} atualizado com sucesso: {msg}")
            messagebox.showinfo("Sucesso", msg); self.atualizar_status(msg, sucesso=True)
            self.limpar_campos_formulario(); self.carregar_alunos_na_tabela()
        else: 
            logger.error(f"Falha ao atualizar aluno ID {id_aluno} (retorno do DB): {msg}")
            messagebox.showerror("Erro ao Atualizar", msg); self.atualizar_status(msg, sucesso=False)

    def deletar_aluno_selecionado(self):
        logger.info("Botão 'Deletar Aluno' clicado.")
        if not self.tree_alunos.focus(): messagebox.showwarning("Nenhuma Seleção", "Selecione um aluno."); return
        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza? Esta ação não pode ser desfeita."):
            logger.info("Deleção cancelada pelo usuário.")
            return
        id_aluno = self.entry_id_var.get()
        if not id_aluno: logger.error("Tentativa de deleção sem ID de aluno."); messagebox.showerror("Erro", "ID do aluno não encontrado."); return
        logger.debug(f"Tentando deletar aluno ID: {id_aluno}")
        sucesso, msg = db_handler.deletar_aluno_db(id_aluno)
        if sucesso:
            logger.info(f"Aluno ID {id_aluno} deletado com sucesso: {msg}")
            messagebox.showinfo("Sucesso", msg); self.atualizar_status(msg, sucesso=True)
            self.limpar_campos_formulario(); self.carregar_alunos_na_tabela()
        else: 
            logger.error(f"Falha ao deletar aluno ID {id_aluno} (retorno do DB): {msg}")
            messagebox.showerror("Erro ao Deletar", msg); self.atualizar_status(msg, sucesso=False)
# --- Fim da classe AplicacaoAlunos ---