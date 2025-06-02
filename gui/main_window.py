# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import db_handler
from datetime import datetime

class AplicacaoAlunos:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Alunos - FacSenac")
        self.root.geometry("1150x700")
        self.root.resizable(True, True)

        # Registra as funções de validação aprimoradas
        self.vcmd_cpf = (self.root.register(self.validar_formato_cpf), '%d', '%P')
        self.vcmd_data = (self.root.register(self.validar_formato_data), '%d', '%P')
        self.vcmd_telefone = (self.root.register(self.validar_formato_telefone), '%d', '%P')
        # Note que só precisamos de '%d' (action) e '%P' (new_value) para esta abordagem

        self.criar_widgets_formulario()
        self.criar_widgets_botoes()
        self.criar_widgets_tabela()
        self.carregar_alunos_na_tabela()

    # --- Funções de Validação Aprimoradas ---
    def validar_formato_cpf(self, action_code, new_value_if_allowed):
        """Valida se o new_value_if_allowed está em conformidade parcial ou total com ###.###.###-##."""
        if action_code == '0':  # Permite deleção
            return True
        
        if len(new_value_if_allowed) > 14:
            return False

        for i, char in enumerate(new_value_if_allowed):
            if i in [3, 7]:  # Posição do ponto
                if char != '.': return False
            elif i == 11:  # Posição do traço
                if char != '-': return False
            else:  # Posição de dígito
                if not char.isdigit(): return False
        return True

    def validar_formato_data(self, action_code, new_value_if_allowed):
        """Valida se o new_value_if_allowed está em conformidade parcial ou total com DD/MM/AAAA."""
        if action_code == '0':  # Permite deleção
            return True

        if len(new_value_if_allowed) > 10:
            return False

        for i, char in enumerate(new_value_if_allowed):
            if i in [2, 5]:  # Posição da barra
                if char != '/': return False
            else:  # Posição de dígito
                if not char.isdigit(): return False
        return True

    def validar_formato_telefone(self, action_code, new_value_if_allowed):
        """Valida se o new_value_if_allowed está em conformidade parcial ou total com (##) #####-####."""
        # Consideraremos o formato de 15 caracteres para celular: (NN) NNNNN-NNNN
        # E o formato de 14 caracteres para fixo: (NN) NNNN-NNNN
        
        if action_code == '0':  # Permite deleção
            return True

        max_len = 15 # Para (##) #####-####
        # Se você quiser ser muito estrito e alternar o max_len baseado no 5º dígito,
        # a lógica se torna mais complexa aqui. Vamos simplificar por enquanto.

        if len(new_value_if_allowed) > max_len:
            return False

        # Validar (NN) NNNNN-NNNN (15 chars)
        # ou    (NN) NNNN-NNNN  (14 chars)
        is_valid = True
        for i, char in enumerate(new_value_if_allowed):
            if i == 0:
                if char != '(': is_valid = False; break
            elif i == 3:
                if char != ')': is_valid = False; break
            elif i == 4: # Espaço após o ')'
                if char != ' ': is_valid = False; break
            elif (max_len == 15 and i == 10) or (max_len == 14 and i == 9): # Posição do traço
                if char != '-': is_valid = False; break
            # Posições dos dígitos (considerando ambos os formatos)
            # Para (NN) NNNNN-NNNN : 1,2, 5,6,7,8,9, 11,12,13,14
            # Para (NN) NNNN-NNNN  : 1,2, 5,6,7,8,   10,11,12,13
            elif i in [1, 2, 5, 6, 7, 8] or \
                 (max_len == 15 and i in [9, 11, 12, 13, 14]) or \
                 (max_len == 14 and i in [10, 11, 12, 13]):
                if not char.isdigit(): is_valid = False; break
            # Caractere em posição não mapeada explicitamente (pode ocorrer se a string for menor que o esperado para um separador)
            # No entanto, a lógica acima deve cobrir os prefixos válidos.
            # Se o caractere atual não é um separador esperado na sua posição E não é um dígito, então é inválido.
            elif char not in "()- " and not char.isdigit():
                is_valid = False; break
        
        if not is_valid:
            # Tentar validar para o formato de 14 caracteres se o de 15 falhou e o comprimento é compatível
            if len(new_value_if_allowed) <= 14:
                is_valid_14 = True
                for i, char in enumerate(new_value_if_allowed):
                    if i == 0:
                        if char != '(': is_valid_14 = False; break
                    elif i == 3:
                        if char != ')': is_valid_14 = False; break
                    elif i == 4: # Espaço
                        if char != ' ': is_valid_14 = False; break
                    elif i == 9: # Traço para 14 char
                        if char != '-': is_valid_14 = False; break
                    elif i in [1, 2, 5, 6, 7, 8, 10, 11, 12, 13]: # Dígitos
                        if not char.isdigit(): is_valid_14 = False; break
                    elif char not in "()- " and not char.isdigit():
                        is_valid_14 = False; break
                return is_valid_14
            return False # Se falhou na de 15 e não é compatível com 14.
            
        return True

    def criar_widgets_formulario(self):
        self.frame_formulario = ttk.LabelFrame(self.root, text="Dados do Aluno", padding=(15, 10))
        self.frame_formulario.pack(padx=10, pady=10, fill="x")

        # Linha 0: ID (sem alteração)
        ttk.Label(self.frame_formulario, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_id_var = tk.StringVar()
        self.entry_id = ttk.Entry(self.frame_formulario, textvariable=self.entry_id_var, width=10, state='readonly')
        self.entry_id.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Linha 1: Nome e Sobrenome (sem alteração)
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
        self.entry_cpf = ttk.Entry(self.frame_formulario, textvariable=self.entry_cpf_var, width=20,
                                   validate="key", validatecommand=self.vcmd_cpf)
        self.entry_cpf.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame_formulario, text="Data Nasc. (DD/MM/AAAA):").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.entry_data_nasc_var = tk.StringVar()
        self.entry_data_nasc = ttk.Entry(self.frame_formulario, textvariable=self.entry_data_nasc_var, width=20,
                                          validate="key", validatecommand=self.vcmd_data)
        self.entry_data_nasc.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        # Linha 3: Telefone e Email
        ttk.Label(self.frame_formulario, text="Telefone ((##) #####-####):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_telefone_var = tk.StringVar()
        self.entry_telefone = ttk.Entry(self.frame_formulario, textvariable=self.entry_telefone_var, width=20,
                                          validate="key", validatecommand=self.vcmd_telefone)
        self.entry_telefone.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame_formulario, text="Email:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.entry_email_var = tk.StringVar()
        self.entry_email = ttk.Entry(self.frame_formulario, textvariable=self.entry_email_var, width=40)
        self.entry_email.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        # Linha 4: Cidade e UF (sem alteração)
        ttk.Label(self.frame_formulario, text="Cidade:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_cidade_var = tk.StringVar(value="Brasília")
        self.entry_cidade = ttk.Entry(self.frame_formulario, textvariable=self.entry_cidade_var, width=30)
        self.entry_cidade.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame_formulario, text="UF:").grid(row=4, column=2, padx=5, pady=5, sticky="w")
        self.entry_uf_var = tk.StringVar(value="DF")
        self.entry_uf = ttk.Entry(self.frame_formulario, textvariable=self.entry_uf_var, width=5)
        self.entry_uf.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        # Linha 5: Curso (sem alteração)
        ttk.Label(self.frame_formulario, text="Curso:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.opcoes_curso = ['ADS', 'GTI', 'CD', 'IA', 'BI', 'SI']
        self.combo_curso_var = tk.StringVar()
        self.combo_curso = ttk.Combobox(self.frame_formulario, textvariable=self.combo_curso_var,
                                        values=self.opcoes_curso, width=37, state="readonly")
        self.combo_curso.grid(row=5, column=1, padx=5, pady=5, sticky="ew", columnspan=1)

        self.frame_formulario.columnconfigure(1, weight=1)
        self.frame_formulario.columnconfigure(3, weight=1)

    #
    # O RESTANTE DAS FUNÇÕES DA CLASSE AplicacaoAlunos CONTINUA IGUAL.
    # (criar_widgets_botoes, criar_widgets_tabela, limpar_campos_formulario,
    # ao_selecionar_item_tabela, carregar_alunos_na_tabela, validar_campos_obrigatorios,
    # _formatar_data_para_db, cadastrar_aluno, atualizar_aluno_selecionado, deletar_aluno_selecionado)
    # COLE-AS AQUI DO SEU CÓDIGO ANTERIOR.
    # A função validar_campos_obrigatorios() ainda fará a checagem final do formato completo.
    #
    def criar_widgets_botoes(self):
        self.frame_botoes = ttk.Frame(self.root, padding=(10, 5))
        self.frame_botoes.pack(fill="x")

        self.btn_cadastrar = ttk.Button(self.frame_botoes, text="Cadastrar",
                                        command=self.cadastrar_aluno, style="Accent.TButton")
        self.btn_cadastrar.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_atualizar = ttk.Button(self.frame_botoes, text="Atualizar", command=self.atualizar_aluno_selecionado)
        self.btn_atualizar.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_deletar = ttk.Button(self.frame_botoes, text="Deletar", command=self.deletar_aluno_selecionado)
        self.btn_deletar.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_limpar = ttk.Button(self.frame_botoes, text="Limpar Campos", command=self.limpar_campos_formulario)
        self.btn_limpar.pack(side=tk.LEFT, padx=5, pady=5)


    def criar_widgets_tabela(self):
        self.frame_tabela = ttk.LabelFrame(self.root, text="Lista de Alunos", padding=(10,10))
        self.frame_tabela.pack(padx=10, pady=10, fill="both", expand=True)

        colunas = ("id", "nome", "sobrenome", "telefone", "email", "cpf", "data_nascimento", "cidade", "uf", "curso")
        self.tree_alunos = ttk.Treeview(self.frame_tabela, columns=colunas, show="headings", height=15)

        for col in colunas:
            text_col = col.replace("_", " ").capitalize()
            if col == "data_nascimento":
                text_col = "Data Nasc."

            self.tree_alunos.heading(col, text=text_col)
            if col == "id": self.tree_alunos.column(col, width=40, minwidth=30, anchor=tk.CENTER)
            elif col == "nome": self.tree_alunos.column(col, width=150, minwidth=100)
            elif col == "sobrenome": self.tree_alunos.column(col, width=150, minwidth=100)
            elif col == "email": self.tree_alunos.column(col, width=180, minwidth=120)
            elif col == "telefone": self.tree_alunos.column(col, width=120, minwidth=100) 
            elif col == "cpf": self.tree_alunos.column(col, width=110, minwidth=90) 
            elif col == "data_nascimento": self.tree_alunos.column(col, width=100, minwidth=80, anchor=tk.CENTER)
            elif col == "cidade": self.tree_alunos.column(col, width=100, minwidth=80)
            elif col == "uf": self.tree_alunos.column(col, width=40, minwidth=30, anchor=tk.CENTER)
            elif col == "curso": self.tree_alunos.column(col, width=70, minwidth=50, anchor=tk.CENTER)
            else: self.tree_alunos.column(col, width=100)

        scrollbar_y = ttk.Scrollbar(self.frame_tabela, orient=tk.VERTICAL, command=self.tree_alunos.yview)
        self.tree_alunos.configure(yscroll=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar_x = ttk.Scrollbar(self.frame_tabela, orient=tk.HORIZONTAL, command=self.tree_alunos.xview)
        self.tree_alunos.configure(xscroll=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree_alunos.pack(fill="both", expand=True)
        self.tree_alunos.bind("<<TreeviewSelect>>", self.ao_selecionar_item_tabela)

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

        valores = self.tree_alunos.item(item_selecionado, "values")
        if valores and len(valores) == 10: 
            self.entry_id_var.set(valores[0])
            self.entry_nome_var.set(valores[1])
            self.entry_sobrenome_var.set(valores[2])
            self.entry_telefone_var.set(valores[3]) 
            self.entry_email_var.set(valores[4])    
            self.entry_cpf_var.set(valores[5])      
            self.entry_data_nasc_var.set(valores[6])
            self.entry_cidade_var.set(valores[7])   
            self.entry_uf_var.set(valores[8])       
            self.combo_curso_var.set(valores[9])    
        elif valores:
            print(f"Aviso: Número inesperado de valores ao selecionar item: {len(valores)}. Esperado 10.")
            self.limpar_campos_formulario(focar_nome=False)


    def carregar_alunos_na_tabela(self):
        for i in self.tree_alunos.get_children():
            self.tree_alunos.delete(i)

        resultados, msg = db_handler.visualizar_alunos_db()
        if resultados is not None:
            for aluno in resultados:
                self.tree_alunos.insert("", tk.END, values=aluno)
        else:
            messagebox.showerror("Erro ao Carregar Alunos", msg)


    def validar_campos_obrigatorios(self): # Validação final
        nome = self.entry_nome_var.get().strip()
        sobrenome = self.entry_sobrenome_var.get().strip()
        curso = self.combo_curso_var.get()
        
        cpf_str = self.entry_cpf_var.get().strip()
        data_nasc_str = self.entry_data_nasc_var.get().strip()
        telefone_str = self.entry_telefone_var.get().strip()

        if not nome or not sobrenome or not curso:
            messagebox.showwarning("Campos Obrigatórios", "Nome, Sobrenome e Curso são obrigatórios.")
            return False
        
        # Validação final de formato completo para campos com máscara
        if cpf_str and not self.validar_formato_cpf('1', cpf_str): # Reutiliza a função de validação
            messagebox.showwarning("Formato Inválido", "Formato final do CPF inválido. Use ###.###.###-##.")
            self.entry_cpf.focus_set()
            return False
        
        if data_nasc_str:
            if not self.validar_formato_data('1', data_nasc_str): # Reutiliza
                messagebox.showwarning("Formato Inválido", "Formato final da Data de Nascimento inválido. Use DD/MM/AAAA.")
                self.entry_data_nasc.focus_set()
                return False
            try: # Validação semântica da data
                datetime.strptime(data_nasc_str, '%d/%m/%Y')
            except ValueError:
                 try:
                    datetime.strptime(data_nasc_str, '%Y-%m-%d')
                 except ValueError:
                    messagebox.showwarning("Data Inválida", "Data de Nascimento inválida (ex: dia ou mês não existe).")
                    self.entry_data_nasc.focus_set()
                    return False
        
        if telefone_str and not self.validar_formato_telefone('1', telefone_str): # Reutiliza
             # A função validar_formato_telefone já é um pouco flexível com 14 ou 15 chars.
             # Podemos adicionar uma verificação mais estrita aqui se o resultado da validação do formato não for exato
             # para os comprimentos 14 ou 15.
            if not (len(telefone_str) == 15 or len(telefone_str) == 14):
                messagebox.showwarning("Formato Inválido", "Formato final do Telefone inválido. Use (##) #####-#### ou (##) ####-####.")
                self.entry_telefone.focus_set()
                return False
        return True

    def _formatar_data_para_db(self, data_str):
        if not data_str:
            return None
        try:
            data_obj = datetime.strptime(data_str, '%d/%m/%Y')
            return data_obj.strftime('%Y-%m-%d')
        except ValueError:
            try:
                datetime.strptime(data_str, '%Y-%m-%d') # Se já estiver no formato do DB
                return data_str 
            except ValueError:
                return None # Ou levante um erro se a validação anterior deveria ter pego


    def cadastrar_aluno(self):
        if not self.validar_campos_obrigatorios():
            return

        cpf_val = self.entry_cpf_var.get().strip()
        data_nasc_db = self._formatar_data_para_db(self.entry_data_nasc_var.get().strip())
        
        dados_aluno = (
            self.entry_nome_var.get().strip(),
            self.entry_sobrenome_var.get().strip(),
            self.entry_telefone_var.get().strip(), 
            self.entry_email_var.get().strip(),    
            cpf_val if cpf_val else None,           
            data_nasc_db,                          
            self.entry_cidade_var.get().strip() if self.entry_cidade_var.get().strip() else 'Brasília',
            self.entry_uf_var.get().strip().upper() if self.entry_uf_var.get().strip() else 'DF',
            self.combo_curso_var.get()
        )

        sucesso, msg = db_handler.cadastrar_aluno_db(dados_aluno)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.limpar_campos_formulario()
            self.carregar_alunos_na_tabela()
        else:
            messagebox.showerror("Erro ao Cadastrar", msg)

    def atualizar_aluno_selecionado(self):
        if not self.tree_alunos.focus():
            messagebox.showwarning("Nenhuma Seleção", "Selecione um aluno na lista para atualizar.")
            return

        if not self.validar_campos_obrigatorios():
            return

        id_aluno = self.entry_id_var.get()
        if not id_aluno:
            messagebox.showerror("Erro", "ID do aluno não encontrado para atualização.")
            return

        cpf_val = self.entry_cpf_var.get().strip()
        data_nasc_db = self._formatar_data_para_db(self.entry_data_nasc_var.get().strip())

        dados_aluno_atualizado = (
            self.entry_nome_var.get().strip(),
            self.entry_sobrenome_var.get().strip(),
            self.entry_telefone_var.get().strip(), 
            self.entry_email_var.get().strip(),    
            cpf_val if cpf_val else None,           
            data_nasc_db,                          
            self.entry_cidade_var.get().strip() if self.entry_cidade_var.get().strip() else 'Brasília',
            self.entry_uf_var.get().strip().upper() if self.entry_uf_var.get().strip() else 'DF',
            self.combo_curso_var.get()
        )

        sucesso, msg = db_handler.atualizar_aluno_db(id_aluno, dados_aluno_atualizado)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.limpar_campos_formulario()
            self.carregar_alunos_na_tabela()
        else:
            messagebox.showerror("Erro ao Atualizar", msg)

    def deletar_aluno_selecionado(self):
        if not self.tree_alunos.focus():
            messagebox.showwarning("Nenhuma Seleção", "Selecione um aluno na lista para deletar.")
            return

        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir este aluno? Esta ação não pode ser desfeita."):
            return

        id_aluno = self.entry_id_var.get()
        if not id_aluno: 
            messagebox.showerror("Erro", "ID do aluno não encontrado para deleção.")
            return

        sucesso, msg = db_handler.deletar_aluno_db(id_aluno)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.limpar_campos_formulario()
            self.carregar_alunos_na_tabela()
        else:
            messagebox.showerror("Erro ao Deletar", msg)