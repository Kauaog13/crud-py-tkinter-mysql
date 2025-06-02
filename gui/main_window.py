# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from database import db_handler
from utils import validators 
from datetime import datetime
import os 
import logging
import re 

logger = logging.getLogger(__name__)

class AplicacaoAlunos:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Alunos - FacSenac")
        self.root.geometry("1250x750") 
        self.root.resizable(True, True)
        logger.info("Janela principal AplicacaoAlunos inicializada.")

        self.is_dark_theme = False 
        self.light_theme = "arc"   
        self.dark_theme = "equilux" 

        self.configurar_estilos_widgets()
        self.carregar_icones() 

        self.coluna_ordenacao_atual = "nome" 
        self.direcao_ordenacao_atual_asc = True 

        self._is_formatting_cpf_programmatically = False

        # --- Definição dos Comandos de Validação ---
        self.vcmd_cpf_char_control = (self.root.register(self.validar_char_cpf_digitacao), '%S', '%d')
        # GARANTIR QUE A LINHA ABAIXO ESTEJA CORRETA E PRESENTE:
        self.vcmd_data_formato = (self.root.register(self.validar_formato_data_digitacao), '%d', '%P') 
        self.vcmd_telefone_formato = (self.root.register(self.validar_formato_telefone_digitacao), '%d', '%P')

        # Ordem de criação dos widgets
        self.criar_widgets_barra_superior()
        self.criar_widgets_formulario() # O erro ocorre aqui se vcmd_data_formato não estiver definido
        self.criar_widgets_busca_filtro() 
        self.criar_widgets_botoes() 
        self.criar_widgets_tabela()
        self.criar_barra_status()

        self.carregar_alunos_na_tabela()

    def configurar_estilos_widgets(self):
        style = ttk.Style()
        style.configure("Valid.TEntry", fieldbackground="lightgreen")
        style.configure("Invalid.TEntry", fieldbackground="#FFCDD2") 
        try:
            default_entry_bg = style.lookup('TEntry', 'fieldbackground')
            style.configure("Normal.TEntry", fieldbackground=default_entry_bg)
        except tk.TclError:
             style.configure("Normal.TEntry", fieldbackground="white")
        logger.debug("Estilos de TEntry para validação configurados.")

    def carregar_icones(self):
        logger.debug("Carregando ícones...")
        base_path = os.path.join(os.path.dirname(__file__), "assets")
        icon_files = { 
            "add": "add.png", "edit": "edit.png", "delete": "delete.png",
            "clear": "clear.png", "theme": "theme_icon.png",
            "export_csv": "export_csv.png"
        }
        self.icons = {}
        for name, filename in icon_files.items():
            path = os.path.join(base_path, filename)
            try: self.icons[name] = tk.PhotoImage(file=path)
            except tk.TclError: logger.warning(f"Ícone '{filename}' não encontrado: {path}"); self.icons[name] = None
    
    def criar_widgets_barra_superior(self):
        logger.debug("Criando widgets da barra superior.")
        self.frame_barra_superior = ttk.Frame(self.root, padding=(5,5))
        self.frame_barra_superior.pack(fill=tk.X, side=tk.TOP, padx=10, pady=(5,0))
        self.btn_toggle_theme = ttk.Button(self.frame_barra_superior, text="Alternar Tema", 
                                           image=self.icons.get("theme"), compound=tk.LEFT if self.icons.get("theme") else tk.NONE,
                                           command=self.alternar_tema)
        self.btn_toggle_theme.pack(side=tk.RIGHT)

    def alternar_tema(self):
        self.is_dark_theme = not self.is_dark_theme
        new_theme = self.dark_theme if self.is_dark_theme else self.light_theme
        logger.info(f"Tentando alterar tema para: {new_theme}")
        try:
            self.root.set_theme(new_theme)
            style = ttk.Style() 
            try:
                default_entry_bg = style.lookup('TEntry', 'fieldbackground')
                style.configure("Normal.TEntry", fieldbackground=default_entry_bg)
            except tk.TclError:
                style.configure("Normal.TEntry", fieldbackground="white") 
            
            fields_to_reset_style = [ 
                getattr(self, 'entry_nome', None), getattr(self, 'entry_sobrenome', None),
                getattr(self, 'entry_email', None), getattr(self, 'entry_cpf', None),
                getattr(self, 'entry_data_nasc', None), getattr(self, 'entry_telefone', None),
                getattr(self, 'entry_cidade', None), getattr(self, 'entry_uf', None)
            ]
            for field in fields_to_reset_style:
                if field and isinstance(field, ttk.Entry): field.configure(style="Normal.TEntry")

            self.atualizar_status(f"Tema alterado para {new_theme}.", duracao_ms=3000)
            logger.info(f"Tema alterado com sucesso para {new_theme}.")
        except tk.TclError as e:
            logger.error(f"Falha ao carregar tema '{new_theme}': {e}")
            messagebox.showwarning("Erro de Tema", f"Não foi possível carregar o tema '{new_theme}'.")
            if new_theme == self.dark_theme: self.is_dark_theme = False

    def validar_char_cpf_digitacao(self, char_inserido, action_code_str):
        action_code = int(action_code_str)
        if self._is_formatting_cpf_programmatically: return True
        if action_code == 0: return True
        if action_code == 1:
            if char_inserido.isdigit():
                current_digits = "".join(filter(str.isdigit, self.entry_cpf_var.get()))
                if len(current_digits) < 11: return True
                else: logger.debug("Máximo de 11 dígitos para CPF atingido."); return False
            else: logger.debug(f"Caractere não dígito '{char_inserido}' bloqueado no CPF."); return False 
        return True

    def formatar_cpf_em_tempo_real(self, event=None):
        if self._is_formatting_cpf_programmatically: return
        self._is_formatting_cpf_programmatically = True
        
        valor_atual_entry = self.entry_cpf_var.get()
        try: cursor_pos_atual = self.entry_cpf.index(tk.INSERT)
        except tk.TclError: cursor_pos_atual = len(valor_atual_entry)

        digitos = "".join(filter(str.isdigit, valor_atual_entry))[:11]
        cpf_formatado = ""
        if len(digitos) > 9: cpf_formatado = f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
        elif len(digitos) > 6: cpf_formatado = f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:]}"
        elif len(digitos) > 3: cpf_formatado = f"{digitos[:3]}.{digitos[3:]}"
        else: cpf_formatado = digitos
        
        self.entry_cpf_var.set(cpf_formatado)

        digitos_antes_cursor_original = 0
        for i in range(min(cursor_pos_atual, len(valor_atual_entry))):
            if valor_atual_entry[i].isdigit(): digitos_antes_cursor_original += 1
        
        nova_pos_cursor = 0; digitos_contados_no_formatado = 0
        for char_formatado in cpf_formatado:
            nova_pos_cursor += 1
            if char_formatado.isdigit(): digitos_contados_no_formatado += 1
            if digitos_contados_no_formatado == digitos_antes_cursor_original:
                if nova_pos_cursor < len(cpf_formatado) and not cpf_formatado[nova_pos_cursor].isdigit():
                    if cursor_pos_atual == nova_pos_cursor -1 : pass 
                    else: nova_pos_cursor +=1 
                break 
        if not digitos: nova_pos_cursor = 0
        nova_pos_cursor = min(nova_pos_cursor, len(cpf_formatado))
        try: self.entry_cpf.icursor(nova_pos_cursor)
        except tk.TclError: logger.debug("Não foi possível definir cursor no CPF (sem foco).")
        
        self.root.after_idle(self._reset_cpf_formatting_flag)
        logger.debug(f"CPF formatado para: {cpf_formatado}, cursor em: {nova_pos_cursor} (tentativa)")

    def _reset_cpf_formatting_flag(self):
        self._is_formatting_cpf_programmatically = False

    # Função de validação para o formato de data DD/MM/AAAA durante a digitação
    def validar_formato_data_digitacao(self, action_code_str, new_value_if_allowed):
        action_code = int(action_code_str) # Convertido para int, embora não usado nesta versão da função
        if new_value_if_allowed == "": return True # Permite apagar completamente
        if len(new_value_if_allowed) > 10: return False # Limita comprimento DD/MM/AAAA

        for i, char in enumerate(new_value_if_allowed):
            if i in [2, 5]: # Posições das barras '/'
                if char != '/': return False
            else: # Outras posições devem ser dígitos
                if not char.isdigit(): return False
        return True

    def validar_formato_telefone_digitacao(self, action_code_str, new_value_if_allowed):
        action_code = int(action_code_str)
        if action_code == 0: return True # Permite deleção
        
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
            elif (max_len == 15 and i == 10) or (max_len == 14 and i == 9): # Traço
                if char != '-': is_valid = False; break
            elif i in [1, 2, 5, 6, 7, 8] or \
                 (max_len == 15 and i in [9, 11, 12, 13, 14]) or \
                 (max_len == 14 and i in [10, 11, 12, 13]): # Dígitos
                if not char.isdigit(): is_valid = False; break
            # Se o caractere não é um separador esperado E não é um dígito, é inválido.
            # Esta checagem também impede que separadores sejam digitados em posições de dígitos.
            elif char not in "()- " and not char.isdigit(): 
                 is_valid = False; break
        
        if not is_valid: # Tenta validar para formato de 14 caracteres se o de 15 falhou
            if len(new_value_if_allowed) <= 14:
                is_valid_14 = True
                for i_14, char_14 in enumerate(new_value_if_allowed):
                    if i_14 == 0:
                        if char_14 != '(': is_valid_14 = False; break
                    elif i_14 == 3:
                        if char_14 != ')': is_valid_14 = False; break
                    elif i_14 == 4:
                        if char_14 != ' ': is_valid_14 = False; break
                    elif i_14 == 9: # Traço para fixo
                        if char_14 != '-': is_valid_14 = False; break
                    elif i_14 in [1, 2, 5, 6, 7, 8, 10, 11, 12, 13]: # Dígitos para fixo
                        if not char_14.isdigit(): is_valid_14 = False; break
                    elif char_14 not in "()- " and not char_14.isdigit():
                         is_valid_14 = False; break
                return is_valid_14
            return False
        return True

    def validar_email_e_atualizar_feedback(self, event=None):
        email_str = self.entry_email_var.get().strip()
        widget = getattr(self, 'entry_email', None)
        if not widget: return 

        if not email_str: widget.configure(style="Normal.TEntry"); return
        valido, msg = validators.validar_email_formato(email_str)
        if valido: widget.configure(style="Valid.TEntry"); logger.debug(f"Email '{email_str}' ok (FocusOut).")
        else: widget.configure(style="Invalid.TEntry"); logger.warning(f"Email '{email_str}' inválido (FocusOut): {msg}")

    def validar_campo_final_e_atualizar_feedback(self, event, nome_campo):
        widget = None; val_str = ""; valido = True; msg_erro = ""
        
        if nome_campo == 'cpf':
            widget = self.entry_cpf; val_str = self.entry_cpf_var.get().strip()
            if val_str: 
                if not re.fullmatch(r"\d{3}\.\d{3}\.\d{3}-\d{2}", val_str): 
                    valido = False; msg_erro = "CPF: Formato final inválido (###.###.###-##)."
                else: 
                    valido, msg_erro = validators.validar_cpf_completo(val_str)
        elif nome_campo == 'data_nasc':
            widget = self.entry_data_nasc; val_str = self.entry_data_nasc_var.get().strip()
            if val_str:
                if not self.validar_formato_data_digitacao('1', val_str): valido = False; msg_erro = "Data Nasc.: Formato DD/MM/AAAA inválido."
                else:
                    try: datetime.strptime(val_str, '%d/%m/%Y')
                    except ValueError: valido = False; msg_erro = "Data Nasc.: Dia ou mês inválido."
                    if valido:
                        data_nasc_db = self._formatar_data_para_db(val_str)
                        if data_nasc_db: valido, msg_erro = validators.validar_data_nascimento_e_idade(data_nasc_db)
                        else: valido = False; msg_erro = "Data Nasc.: Erro interno de formatação para idade."
        elif nome_campo == 'telefone':
            widget = self.entry_telefone; val_str = self.entry_telefone_var.get().strip()
            if val_str: 
                valido, msg_erro = validators.validar_telefone_formato(val_str) # Usa validador de backend para formato final

        if widget: # Aplica feedback se o campo não estiver vazio (val_str foi preenchido)
            if not val_str: # Se o campo ficou vazio após FocusOut, reseta para Normal
                 widget.configure(style="Normal.TEntry")
            elif valido: 
                widget.configure(style="Valid.TEntry")
                logger.debug(f"Campo '{nome_campo}' ('{val_str}') OK (FocusOut).")
            else: 
                widget.configure(style="Invalid.TEntry")
                logger.warning(f"Campo '{nome_campo}' ('{val_str}') Inválido (FocusOut): {msg_erro}")
    
    def criar_widgets_formulario(self):
        logger.debug("Criando widgets do formulário.")
        self.frame_formulario = ttk.LabelFrame(self.root, text="Dados do Aluno", padding=(15, 10))
        self.frame_formulario.pack(padx=10, pady=(0,10), fill="x", side=tk.TOP)
        
        ttk.Label(self.frame_formulario, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_id_var = tk.StringVar()
        self.entry_id = ttk.Entry(self.frame_formulario, textvariable=self.entry_id_var, width=10, state='readonly', style="TEntry")
        self.entry_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame_formulario, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_nome_var = tk.StringVar()
        self.entry_nome = ttk.Entry(self.frame_formulario, textvariable=self.entry_nome_var, width=40, style="Normal.TEntry")
        self.entry_nome.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.frame_formulario, text="Sobrenome:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_sobrenome_var = tk.StringVar()
        self.entry_sobrenome = ttk.Entry(self.frame_formulario, textvariable=self.entry_sobrenome_var, width=40, style="Normal.TEntry")
        self.entry_sobrenome.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame_formulario, text="CPF (auto-formata):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_cpf_var = tk.StringVar()
        self.entry_cpf = ttk.Entry(self.frame_formulario, textvariable=self.entry_cpf_var, width=20,
                                   validate="key", validatecommand=self.vcmd_cpf_char_control, style="Normal.TEntry")
        self.entry_cpf.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.entry_cpf.bind("<KeyRelease>", self.formatar_cpf_em_tempo_real) 
        self.entry_cpf.bind("<FocusOut>", lambda event, field_name="cpf": self.validar_campo_final_e_atualizar_feedback(event, field_name))

        ttk.Label(self.frame_formulario, text="Data Nasc. (DD/MM/AAAA):").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.entry_data_nasc_var = tk.StringVar()
        self.entry_data_nasc = ttk.Entry(self.frame_formulario, textvariable=self.entry_data_nasc_var, width=20,
                                          validate="key", validatecommand=self.vcmd_data_formato, style="Normal.TEntry")
        self.entry_data_nasc.grid(row=2, column=3, padx=5, pady=5, sticky="ew")
        self.entry_data_nasc.bind("<FocusOut>", lambda event, field_name="data_nasc": self.validar_campo_final_e_atualizar_feedback(event, field_name))

        ttk.Label(self.frame_formulario, text="Telefone ((##) #####-####):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_telefone_var = tk.StringVar()
        self.entry_telefone = ttk.Entry(self.frame_formulario, textvariable=self.entry_telefone_var, width=20,
                                          validate="key", validatecommand=self.vcmd_telefone_formato, style="Normal.TEntry")
        self.entry_telefone.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.entry_telefone.bind("<FocusOut>", lambda event, field_name="telefone": self.validar_campo_final_e_atualizar_feedback(event, field_name))

        ttk.Label(self.frame_formulario, text="Email:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.entry_email_var = tk.StringVar()
        self.entry_email = ttk.Entry(self.frame_formulario, textvariable=self.entry_email_var, width=40, style="Normal.TEntry")
        self.entry_email.grid(row=3, column=3, padx=5, pady=5, sticky="ew")
        self.entry_email.bind("<FocusOut>", self.validar_email_e_atualizar_feedback)

        ttk.Label(self.frame_formulario, text="Cidade:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_cidade_var = tk.StringVar(value="Brasília")
        self.entry_cidade = ttk.Entry(self.frame_formulario, textvariable=self.entry_cidade_var, width=30, style="Normal.TEntry")
        self.entry_cidade.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(self.frame_formulario, text="UF:").grid(row=4, column=2, padx=5, pady=5, sticky="w")
        self.entry_uf_var = tk.StringVar(value="DF")
        self.entry_uf = ttk.Entry(self.frame_formulario, textvariable=self.entry_uf_var, width=5, style="Normal.TEntry")
        self.entry_uf.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(self.frame_formulario, text="Curso:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.opcoes_curso = ['ADS', 'GTI', 'CD', 'IA', 'BI', 'SI']
        self.combo_curso_var = tk.StringVar()
        self.combo_curso = ttk.Combobox(self.frame_formulario, textvariable=self.combo_curso_var, values=self.opcoes_curso, width=37, state="readonly", style="TCombobox")
        self.combo_curso.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        self.frame_formulario.columnconfigure(1, weight=1); self.frame_formulario.columnconfigure(3, weight=1)

    # --- Definição de criar_widgets_busca_filtro ---
    def criar_widgets_busca_filtro(self):
        logger.debug("Criando widgets de busca/filtro.")
        self.frame_busca = ttk.LabelFrame(self.root, text="Busca e Filtro", padding=(10,5))
        self.frame_busca.pack(padx=10, pady=(0,5), fill="x", side=tk.TOP)
        ttk.Label(self.frame_busca, text="Buscar por:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_field_options = ["Nome", "Sobrenome", "CPF", "Email", "Curso", "Cidade", "UF"]
        self.search_field_var = tk.StringVar(value=self.search_field_options[0])
        self.combo_search_field = ttk.Combobox(self.frame_busca, textvariable=self.search_field_var, values=self.search_field_options, state="readonly", width=15)
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
        logger.debug("Criando widgets de botões (CRUD e Exportar).")
        self.frame_botoes = ttk.Frame(self.root, padding=(10, 5))
        self.frame_botoes.pack(fill="x", side=tk.TOP, padx=10, pady=(0,5))
        compound_pos = tk.LEFT 
        self.btn_cadastrar = ttk.Button(self.frame_botoes, text="Cadastrar", image=self.icons.get("add"), compound=compound_pos, command=self.cadastrar_aluno, style="TButton")
        self.btn_cadastrar.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_atualizar = ttk.Button(self.frame_botoes, text="Atualizar", image=self.icons.get("edit"), compound=compound_pos, command=self.atualizar_aluno_selecionado, style="TButton")
        self.btn_atualizar.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_deletar = ttk.Button(self.frame_botoes, text="Deletar", image=self.icons.get("delete"), compound=compound_pos, command=self.deletar_aluno_selecionado, style="TButton")
        self.btn_deletar.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar Campos", image=self.icons.get("clear"), compound=compound_pos, command=self.limpar_campos_formulario, style="TButton")
        self.btn_limpar.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_exportar_csv = ttk.Button(self.frame_botoes, text="Exportar CSV", image=self.icons.get("export_csv"), compound=compound_pos, command=self.exportar_para_csv, style="TButton")
        self.btn_exportar_csv.pack(side=tk.LEFT, padx=15, pady=5)

    def criar_widgets_tabela(self):
        logger.debug("Criando widget da tabela (Treeview).")
        self.frame_tabela = ttk.LabelFrame(self.root, text="Lista de Alunos", padding=(10,10))
        self.frame_tabela.pack(padx=10, pady=5, fill="both", expand=True, side=tk.TOP)
        self.map_coluna_cabecalho = { "id": "ID", "nome": "Nome", "sobrenome": "Sobrenome", "telefone": "Telefone", "email": "E-mail", "cpf": "CPF", "data_nascimento_formatada": "Data Nasc.", "cidade": "Cidade", "uf": "UF", "curso": "Curso" }
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
        if duracao_ms > 0: self.root.after(duracao_ms, lambda: self.status_var.set("Pronto"))

    def executar_busca(self, event=None):
        campo = self.search_field_var.get(); termo = self.search_term_var.get().strip()
        logger.info(f"Executando busca: Campo='{campo}', Termo='{termo}'")
        if not termo: self.limpar_busca(); return
        self.carregar_alunos_na_tabela(search_field=campo, search_term=termo, sort_by_column=self.coluna_ordenacao_atual, sort_direction='ASC' if self.direcao_ordenacao_atual_asc else 'DESC')
        self.atualizar_status(f"Buscando por '{termo}' em '{campo}'.")

    def limpar_busca(self):
        logger.info("Limpando busca.")
        self.search_term_var.set("")
        self.carregar_alunos_na_tabela(sort_by_column=self.coluna_ordenacao_atual, sort_direction='ASC' if self.direcao_ordenacao_atual_asc else 'DESC')
        self.atualizar_status("Busca limpa. Exibindo todos os alunos."); self.entry_search_term.focus_set()

    def ordenar_coluna_tabela(self, coluna_clicada_db):
        if coluna_clicada_db == self.coluna_ordenacao_atual: self.direcao_ordenacao_atual_asc = not self.direcao_ordenacao_atual_asc
        else: self.coluna_ordenacao_atual = coluna_clicada_db; self.direcao_ordenacao_atual_asc = True
        direcao = 'ASC' if self.direcao_ordenacao_atual_asc else 'DESC'
        logger.info(f"Ordenando tabela por '{coluna_clicada_db}' na direção '{direcao}'.")
        campo_busca_atual = self.search_field_var.get(); termo_busca_atual = self.search_term_var.get().strip()
        self.carregar_alunos_na_tabela(search_field=campo_busca_atual if termo_busca_atual else None, search_term=termo_busca_atual if termo_busca_atual else None, sort_by_column=self.coluna_ordenacao_atual, sort_direction=direcao )
        nome_exibicao_coluna = coluna_clicada_db.capitalize()
        for key_visual, texto_cabecalho in self.map_coluna_cabecalho.items():
            db_col = "data_nascimento" if key_visual == "data_nascimento_formatada" else key_visual
            if coluna_clicada_db == db_col: nome_exibicao_coluna = texto_cabecalho; break
        self.atualizar_status(f"Ordenado por {nome_exibicao_coluna} ({direcao.lower()}).")

    def limpar_campos_formulario(self, focar_nome=True):
        logger.debug("Limpando campos do formulário e resetando estilos.")
        self.entry_id_var.set(""); self.entry_nome_var.set(""); self.entry_sobrenome_var.set("")
        self.entry_cpf_var.set(""); self.entry_data_nasc_var.set(""); self.entry_telefone_var.set("")
        self.entry_email_var.set(""); self.entry_cidade_var.set("Brasília"); self.entry_uf_var.set("DF")
        self.combo_curso_var.set("")
        for attr_name in ['entry_nome', 'entry_sobrenome', 'entry_cpf', 'entry_data_nasc', 'entry_telefone', 'entry_email', 'entry_cidade', 'entry_uf']:
            widget = getattr(self, attr_name, None)
            if widget and isinstance(widget, ttk.Entry): widget.configure(style="Normal.TEntry")
        if focar_nome and hasattr(self, 'entry_nome'): self.entry_nome.focus_set()
        selecao = self.tree_alunos.selection()
        if selecao: self.tree_alunos.selection_remove(selecao)

    def ao_selecionar_item_tabela(self, event=None):
        item_selecionado = self.tree_alunos.focus()
        if not item_selecionado: return
        valores_linha = self.tree_alunos.item(item_selecionado, "values")
        if valores_linha and len(valores_linha) == 10:
            logger.debug(f"Item selecionado na tabela: ID={valores_linha[0]}, Nome='{valores_linha[1]}'")
            self.entry_id_var.set(str(valores_linha[0])); self.entry_nome_var.set(str(valores_linha[1]))
            self.entry_sobrenome_var.set(str(valores_linha[2])); self.entry_telefone_var.set(str(valores_linha[3]))
            self.entry_email_var.set(str(valores_linha[4])); self.entry_cpf_var.set(str(valores_linha[5]))
            self.entry_data_nasc_var.set(str(valores_linha[6])); self.entry_cidade_var.set(str(valores_linha[7]))
            self.entry_uf_var.set(str(valores_linha[8])); self.combo_curso_var.set(str(valores_linha[9]))
            for attr_name in ['entry_cpf', 'entry_data_nasc', 'entry_telefone', 'entry_email']:
                widget = getattr(self, attr_name, None)
                if widget and isinstance(widget, ttk.Entry): widget.configure(style="Normal.TEntry")
        elif valores_linha:
            logger.warning(f"Discrepância de valores ao selecionar. Recebido: {len(valores_linha)}, Esperado: 10.")
            self.limpar_campos_formulario(focar_nome=False)

    def carregar_alunos_na_tabela(self, search_field=None, search_term=None, sort_by_column=None, sort_direction='ASC'):
        logger.info(f"Carregando alunos: busca='{search_field}':'{search_term}', ordenar='{sort_by_column}':'{sort_direction}'")
        for i in self.tree_alunos.get_children(): self.tree_alunos.delete(i)
        if sort_by_column is None:
            sort_by_column = self.coluna_ordenacao_atual
            sort_direction = 'ASC' if self.direcao_ordenacao_atual_asc else 'DESC'
        resultados, msg_status_db = db_handler.visualizar_alunos_db(search_field=search_field, search_term=search_term, sort_by_column=sort_by_column, sort_direction=sort_direction)
        if resultados is not None:
            logger.debug(f"{len(resultados)} alunos retornados do DB.")
            for aluno in resultados: self.tree_alunos.insert("", tk.END, values=aluno)
            if "Erro" not in msg_status_db : self.atualizar_status(msg_status_db if msg_status_db else f"{len(resultados)} alunos carregados.")
            else: self.atualizar_status(msg_status_db, sucesso=False)
        else:
            logger.error(f"Falha ao carregar alunos do DB: {msg_status_db}")
            messagebox.showerror("Erro ao Carregar Alunos", msg_status_db)
            self.atualizar_status(msg_status_db if msg_status_db else "Falha ao carregar alunos.", sucesso=False)

    def validar_campos_obrigatorios(self):
        logger.debug("Executando validação final de campos obrigatórios e formatos.")
        def aplicar_feedback_e_falhar(widget_attr_name, mensagem_erro, nome_campo_log): # Helper
            widget = getattr(self, widget_attr_name, None)
            if widget and isinstance(widget, ttk.Entry): widget.configure(style="Invalid.TEntry"); widget.focus_set()
            logger.warning(f"Validação GUI falhou para '{nome_campo_log}': {mensagem_erro}")
            messagebox.showwarning("Validação Falhou", mensagem_erro); return False
        
        for attr_name in ['entry_nome', 'entry_sobrenome', 'entry_cpf', 'entry_data_nasc', 'entry_telefone', 'entry_email', 'entry_cidade', 'entry_uf']:
            widget = getattr(self, attr_name, None)
            if widget and isinstance(widget, ttk.Entry): widget.configure(style="Normal.TEntry")
        
        nome=self.entry_nome_var.get().strip(); sobrenome=self.entry_sobrenome_var.get().strip(); curso=self.combo_curso_var.get()
        cpf_str=self.entry_cpf_var.get().strip(); data_nasc_str_gui=self.entry_data_nasc_var.get().strip()
        telefone_str=self.entry_telefone_var.get().strip(); email_str=self.entry_email_var.get().strip()

        if not nome or not sobrenome or not curso: messagebox.showwarning("Campos Obrigatórios", "Nome, Sobrenome e Curso são obrigatórios."); return False
        
        if cpf_str:
            if not re.fullmatch(r"\d{3}\.\d{3}\.\d{3}-\d{2}", cpf_str): return aplicar_feedback_e_falhar('entry_cpf', "CPF: Formato inválido (###.###.###-##).", "CPF_Mascara_Final")
            valido_cpf_alg, msg_cpf_alg = validators.validar_cpf_completo(cpf_str)
            if not valido_cpf_alg: return aplicar_feedback_e_falhar('entry_cpf', msg_cpf_alg, "CPF_Algoritmo")
            self.entry_cpf.configure(style="Valid.TEntry")
        
        if email_str:
            valido_email, msg_email = validators.validar_email_formato(email_str)
            if not valido_email: return aplicar_feedback_e_falhar('entry_email', msg_email, "Email")
            self.entry_email.configure(style="Valid.TEntry")

        if telefone_str:
            valido_tel, msg_tel = validators.validar_telefone_formato(telefone_str)
            if not valido_tel: return aplicar_feedback_e_falhar('entry_telefone', msg_tel, "Telefone")
            self.entry_telefone.configure(style="Valid.TEntry")
        
        if data_nasc_str_gui:
            if not self.validar_formato_data_digitacao('1', data_nasc_str_gui): return aplicar_feedback_e_falhar('entry_data_nasc', "Data Nasc.: Formato DD/MM/AAAA inválido.", "DataNasc_Mascara")
            try: datetime.strptime(data_nasc_str_gui, '%d/%m/%Y')
            except ValueError: return aplicar_feedback_e_falhar('entry_data_nasc', "Data Nasc.: Dia ou mês inválido.", "DataNasc_Semantica")
            data_nasc_para_backend = self._formatar_data_para_db(data_nasc_str_gui)
            if data_nasc_para_backend:
                valido_idade, msg_idade = validators.validar_data_nascimento_e_idade(data_nasc_para_backend)
                if not valido_idade: return aplicar_feedback_e_falhar('entry_data_nasc', msg_idade, "DataNasc_Idade")
            else: return aplicar_feedback_e_falhar('entry_data_nasc', "Data Nasc.: Erro interno de formatação.", "DataNasc_FormatacaoInterna")
            self.entry_data_nasc.configure(style="Valid.TEntry")

        logger.debug("Validação final de campos na GUI passou.")
        return True

    def _formatar_data_para_db(self, data_str_ddmmyyyy):
        if not data_str_ddmmyyyy: return None
        try: data_obj = datetime.strptime(data_str_ddmmyyyy, '%d/%m/%Y'); return data_obj.strftime('%Y-%m-%d')
        except ValueError:
            try: datetime.strptime(data_str_ddmmyyyy, '%Y-%m-%d'); return data_str_ddmmyyyy
            except ValueError: logger.warning(f"Data '{data_str_ddmmyyyy}' não pôde ser formatada para o BD."); return None

    def cadastrar_aluno(self):
        logger.info("Botão 'Cadastrar Aluno' clicado.")
        if not self.validar_campos_obrigatorios(): logger.warning("Cadastro abortado: falha na validação da GUI."); return
        dados_aluno = ( self.entry_nome_var.get().strip(), self.entry_sobrenome_var.get().strip(), self.entry_telefone_var.get().strip() or None, self.entry_email_var.get().strip() or None, self.entry_cpf_var.get().strip() or None, self._formatar_data_para_db(self.entry_data_nasc_var.get().strip()), self.entry_cidade_var.get().strip() or 'Brasília', self.entry_uf_var.get().strip().upper() or 'DF', self.combo_curso_var.get() )
        logger.debug(f"Dados para cadastro: {dados_aluno}")
        sucesso, msg = db_handler.cadastrar_aluno_db(dados_aluno)
        if sucesso: logger.info(f"Aluno cadastrado: {msg}"); messagebox.showinfo("Sucesso", msg); self.atualizar_status(msg, sucesso=True); self.limpar_campos_formulario(); self.carregar_alunos_na_tabela()
        else: logger.error(f"Falha ao cadastrar (DB): {msg}"); messagebox.showerror("Erro ao Cadastrar", msg); self.atualizar_status(msg, sucesso=False)

    def atualizar_aluno_selecionado(self):
        logger.info("Botão 'Atualizar Aluno' clicado.")
        if not self.tree_alunos.focus(): messagebox.showwarning("Nenhuma Seleção", "Selecione um aluno."); return
        if not self.validar_campos_obrigatorios(): logger.warning("Atualização abortada: falha na validação da GUI."); return
        id_aluno = self.entry_id_var.get()
        if not id_aluno: logger.error("Atualização sem ID."); messagebox.showerror("Erro", "ID do aluno não encontrado."); return
        dados_aluno_atualizado = ( self.entry_nome_var.get().strip(), self.entry_sobrenome_var.get().strip(), self.entry_telefone_var.get().strip() or None, self.entry_email_var.get().strip() or None, self.entry_cpf_var.get().strip() or None, self._formatar_data_para_db(self.entry_data_nasc_var.get().strip()), self.entry_cidade_var.get().strip() or 'Brasília', self.entry_uf_var.get().strip().upper() or 'DF', self.combo_curso_var.get() )
        logger.debug(f"Dados para atualização (ID: {id_aluno}): {dados_aluno_atualizado}")
        sucesso, msg = db_handler.atualizar_aluno_db(id_aluno, dados_aluno_atualizado)
        if sucesso: logger.info(f"Aluno ID {id_aluno} atualizado: {msg}"); messagebox.showinfo("Sucesso", msg); self.atualizar_status(msg, sucesso=True); self.limpar_campos_formulario(); self.carregar_alunos_na_tabela()
        else: logger.error(f"Falha ao atualizar ID {id_aluno} (DB): {msg}"); messagebox.showerror("Erro ao Atualizar", msg); self.atualizar_status(msg, sucesso=False)

    def deletar_aluno_selecionado(self):
        logger.info("Botão 'Deletar Aluno' clicado.")
        if not self.tree_alunos.focus(): messagebox.showwarning("Nenhuma Seleção", "Selecione um aluno."); return
        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza? Esta ação não pode ser desfeita."): logger.info("Deleção cancelada."); return
        id_aluno = self.entry_id_var.get()
        if not id_aluno: logger.error("Deleção sem ID."); messagebox.showerror("Erro", "ID do aluno não encontrado."); return
        logger.debug(f"Tentando deletar aluno ID: {id_aluno}")
        sucesso, msg = db_handler.deletar_aluno_db(id_aluno)
        if sucesso: logger.info(f"Aluno ID {id_aluno} deletado: {msg}"); messagebox.showinfo("Sucesso", msg); self.atualizar_status(msg, sucesso=True); self.limpar_campos_formulario(); self.carregar_alunos_na_tabela()
        else: logger.error(f"Falha ao deletar ID {id_aluno} (DB): {msg}"); messagebox.showerror("Erro ao Deletar", msg); self.atualizar_status(msg, sucesso=False)

    def exportar_para_csv(self):
        logger.info("Botão 'Exportar CSV' clicado.")
        caminho_arquivo = filedialog.asksaveasfilename( defaultextension=".csv", filetypes=[("Arquivo CSV", "*.csv"), ("Todos os arquivos", "*.*")], title="Salvar lista de alunos como CSV", initialfile="alunos_exportados.csv" )
        if not caminho_arquivo: logger.info("Exportação CSV cancelada."); self.atualizar_status("Exportação cancelada.", duracao_ms=3000); return
        try:
            if not self.tree_alunos.get_children(): messagebox.showinfo("Exportar CSV", "Não há dados para exportar."); logger.info("Exportar CSV: sem dados."); return
            ordem_dados_db = ["id", "nome", "sobrenome", "telefone", "email", "cpf", "data_nascimento_formatada", "cidade", "uf", "curso"]
            cabecalhos = [self.map_coluna_cabecalho.get(col_key, col_key.capitalize()) for col_key in ordem_dados_db]
            alunos_para_exportar = [[str(v) if v is not None else "" for v in self.tree_alunos.item(item_id)["values"]] for item_id in self.tree_alunos.get_children()]
            if not alunos_para_exportar: messagebox.showinfo("Exportar CSV", "Não há dados para exportar."); return
            with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
                escritor_csv = csv.writer(arquivo_csv, delimiter=';')
                escritor_csv.writerow(cabecalhos); logger.debug(f"Exportando cabeçalhos CSV: {cabecalhos}")
                for aluno_tupla in alunos_para_exportar: escritor_csv.writerow(aluno_tupla)
            logger.info(f"Dados exportados para CSV: {caminho_arquivo}")
            messagebox.showinfo("Exportação Concluída", f"Alunos exportados para:\n{caminho_arquivo}"); self.atualizar_status("Dados exportados para CSV!", sucesso=True)
        except IOError as e: logger.error(f"Erro de E/S ao exportar CSV: {e}", exc_info=True); messagebox.showerror("Erro de Exportação", f"Não foi possível salvar o arquivo CSV.\nDetalhe: {e}"); self.atualizar_status("Falha ao exportar CSV.", sucesso=False)
        except Exception as e: logger.exception(f"Erro inesperado ao exportar CSV"); messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado.\nDetalhe: {e}"); self.atualizar_status("Erro na exportação.", sucesso=False)
# --- Fim da classe AplicacaoAlunos ---