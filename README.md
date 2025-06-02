# 🧑‍🎓 Sistema de Cadastro de Alunos - FacSenac 🧑‍🎓

Este é um projeto de um sistema de Gerenciamento de Cadastro de Alunos (CRUD completo) desenvolvido em Python, com interface gráfica utilizando Tkinter e ttkthemes, e banco de dados MySQL. A aplicação permite criar, visualizar, atualizar, deletar, buscar, filtrar, ordenar e exportar registros de alunos. 📝

## Funcionalidades Principais ✨

* **CRUD Completo:** Cadastrar, Visualizar, Atualizar e Deletar (CRUD) informações de alunos.
* **Interface Gráfica Amigável:** Construída com Tkinter e `ttkthemes` para uma aparência moderna.
* **Campos do Aluno:** ID (auto-incremento), Nome, Sobrenome, CPF, Data de Nascimento, Telefone, Email, Cidade (padrão 'Brasília'), UF (padrão 'DF'), Curso (lista de opções).
* **Validação de Dados:**
    * Validação robusta para CPF (usando `validate-docbr`, com opção para desativar verificação de dígitos para testes).
    * Validação de formato para Email e Telefone usando expressões regulares.
    * Validação de idade mínima para Data de Nascimento (aluno não pode ter menos de 17 anos).
    * Máscaras de entrada para CPF (auto-formatação), Data de Nascimento e Telefone (formato guiado).
    * Feedback visual em tempo real para validação de campos (ao perder o foco).
* **Busca e Filtro Avançados:** Permite buscar alunos por diversos campos (Nome, CPF, Curso, etc.).
* **Ordenação da Lista:** Clique nos cabeçalhos das colunas na tabela de alunos para ordenar os dados.
* **Exportação para CSV:** Exporte a lista de alunos (visível na tabela) para um arquivo CSV.
* **Temas:** Botão para alternar entre tema claro ("arc") e escuro ("equilux").
* **Ícones:** Ícones visuais nos botões de ação para melhor usabilidade.
* **Barra de Status:** Exibe mensagens informativas sobre as operações realizadas.
* **Logging:** Registra eventos da aplicação, erros e informações de debug em um arquivo `app_alunos.log` para facilitar o diagnóstico.
* **Configuração Segura:** Utiliza arquivo `.env` para armazenar credenciais do banco de dados e outras configurações sensíveis, mantendo-as fora do código-fonte.

## Tecnologias, Linguagens e Bibliotecas Utilizadas 🛠️

* **Linguagem:** Python 3.x
* **Interface Gráfica (GUI):**
    * Tkinter (biblioteca padrão do Python)
    * `ttkthemes` (para aplicar temas modernos aos widgets ttk)
* **Banco de Dados:**
    * MySQL Server
    * `mysql-connector-python` (biblioteca para conectar Python ao MySQL)
* **Validação de Dados:**
    * `validate-docbr` (para validação algorítmica de CPF)
    * Módulo `re` (para expressões regulares - Email, Telefone)
* **Manipulação de Dados e Arquivos:**
    * Módulo `csv` (para exportação de dados)
    * Módulo `datetime` (para manipulação de datas e cálculo de idade)
    * Módulo `os` (para manipulação de caminhos de arquivo)
* **Gerenciamento de Configuração:**
    * `python-dotenv` (para carregar variáveis de ambiente do arquivo `.env`)
* **Logging:**
    * Módulo `logging` (biblioteca padrão do Python)

## Estrutura do Projeto 📂

crud-py-tkinter-mysql/
├── app_alunos.py             # Ponto de entrada principal da aplicação  
├── database/  
│   ├── init.py  
│   ├── db_config.py          # Carrega configurações do BD a partir do .env  
│   ├── db_handler.py         # Lógica de interação com o banco de dados (CRUD)  
│   └── schema.sql            # Script SQL para criar o banco e a tabela  
├── gui/  
│   ├── init.py  
│   ├── main_window.py        # Constrói e gerencia a interface gráfica principal  
│   └── assets/               # Contém os ícones utilizados na GUI  
│       ├── add.png  
│       ├── edit.png  
│       ├── delete.png  
│       ├── clear.png  
│       ├── theme_icon.png  
│       └── export_csv.png  
├── utils/  
│   ├── init.py  
│   └── validators.py         # Funções de validação de dados (CPF, email, etc.)  
├── .env.example              # Arquivo de exemplo para o .env (NÃO COMITAR O .env REAL COM SENHAS)  
├── .gitignore                # Especifica arquivos e pastas ignorados pelo Git  
├── README.md                 # Este arquivo  
└── requirements.txt          # Lista de dependências do projeto  
└── app_alunos.log            # Arquivo de log gerado pela aplicação (ignorado pelo .gitignore)  

## Passo a Passo: Clonar e Utilizar o Projeto 🚀

Siga estas instruções para configurar e executar o projeto em seu ambiente local.

### 1. Pré-requisitos
* **Python 3.x:** Certifique-se de ter o Python instalado. Você pode baixá-lo em [python.org](https://www.python.org/downloads/).
* **MySQL Server:** Você precisa de uma instância do MySQL Server rodando. Você pode usar o MySQL Community Server, XAMPP, WAMP, Docker, etc.
* **Git:** Para clonar o repositório (se estiver em um).

### 2. Clonar o Repositório (Opcional)
↕️Se o projeto estiver em um repositório Git, clone-o:
```bash
git clone https://github.com/Kauaog13/crud-py-tkinter-mysql.git
cd crud-py-tkinter-mysql
```

### 3. Instalar Dependências
📤 Com o ambiente virtual ativado, instale as bibliotecas listadas no requirements.txt:

```Bash
pip install -r requirements.txt
```
O arquivo requirements.txt deve conter:

- mysql-connector-python  
- ttkthemes  
- python-dotenv  
- messagebox  
- validate-docbr
  
Observação: messagebox faz parte do tkinter e não precisa ser listado no requirements.txt para instalação via pip.

### 4. Configurar o Banco de Dados MySQL
🗂️Crie o Banco de Dados facsenac e conecte-se ao servidor
```Bash
CREATE DATABASE IF NOT EXISTS facsenac DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE facsenac;

CREATE TABLE IF NOT EXISTS alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    sobrenome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    cpf VARCHAR(14) UNIQUE,     
    data_nascimento DATE,        
    cidade VARCHAR(100) DEFAULT 'Brasília',
    uf VARCHAR(2) DEFAULT 'DF',
    curso ENUM('ADS', 'GTI', 'CD', 'IA', 'BI', 'SI') NOT NULL
);
```

### 5. Configurar o Arquivo .env (Muito Importante!)
Este arquivo armazena suas credenciais de banco de dados e outras configurações de forma segura, fora do código.  
🔒 Na pasta raiz do seu projeto (ex: crud-py-tkinter-mysql/), crie um arquivo chamado exatamente .env.
```Bash
DB_HOST=[seu_local_host]
DB_USER=[seu_usuario]
DB_PASSWORD=[sua_senha]
DB_NAME=facsenac

VALIDATE_CPF_STRICTLY=[True] or [False]
```
* **`DB_HOST`**: Geralmente `localhost` se o MySQL estiver rodando na sua máquina.
* **`DB_USER`**: Seu nome de usuário do MySQL (ex: `root` para desenvolvimento local, mas um usuário dedicado é melhor para produção).
* **`DB_PASSWORD`**: A senha do seu usuário MySQL.
* **`DB_NAME`**: O nome do banco de dados que você criou (ex: `facsenac`).
* **`VALIDATE_CPF_STRICTLY`**: Controla se a validação completa do CPF (dígitos verificadores) é realizada.

### 6. Executar a Aplicação
Com o ambiente virtual ativado (se estiver usando um) e todas as configurações feitas, navegue até a pasta raiz do projeto no seu terminal e execute:
```Bash
python app_alunos.py
```
✔️ A interface gráfica do Sistema de Cadastro de Alunos deve iniciar.

## Troubleshooting e Notas Adicionais

- Arquivo de Log: A aplicação gera um arquivo de log chamado app_alunos.log na pasta raiz do projeto. Consulte este arquivo para mensagens de erro detalhadas e informações de depuração.  
- Ícones: Os ícones da interface são carregados da pasta gui/assets/. Se algum ícone estiver faltando, um aviso será logado no console e o botão correspondente aparecerá sem imagem.  
- Exportação CSV: Os arquivos CSV são exportados usando ponto e vírgula (;) como delimitador, o que é comum no Brasil para melhor compatibilidade com o Excel. Se você abrir o CSV no Excel e os dados aparecerem em uma única coluna, use a opção "Dados" > "De Texto/CSV" e especifique "Ponto e vírgula" como delimitador na janela de importação.  
- Validação de CPF: Se VALIDATE_CPF_STRICTLY estiver False no .env, você poderá cadastrar CPFs com dígitos verificadores inválidos, desde que o formato da máscara (###.###.###-##) seja respeitado.  
