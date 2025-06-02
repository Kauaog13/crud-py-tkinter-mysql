# database/db_handler.py
import mysql.connector
from tkinter import messagebox # Mantido para erros críticos se houver
from . import db_config

def conectar_db():
    """Conecta ao banco de dados MySQL especificado em db_config."""
    try:
        conexao = mysql.connector.connect(
            host=db_config.DB_HOST,
            user=db_config.DB_USER,
            password=db_config.DB_PASSWORD,
            database=db_config.DB_NAME
        )
        return conexao
    except mysql.connector.Error as err:
        print(f"Erro de Conexão com o BD: {err}")
        return None

# Função visualizar_alunos_db MODIFICADA para busca e ordenação
def visualizar_alunos_db(search_field=None, search_term=None, sort_by_column=None, sort_direction='ASC'):
    """
    Busca alunos no banco de dados com opções de busca e ordenação.
    Retorna (resultados, mensagem_status).
    """
    conexao = conectar_db()
    if not conexao:
        return None, "Falha na conexão com o banco de dados."

    cursor = conexao.cursor()
    
    # Colunas permitidas para busca e ordenação (para segurança contra SQL Injection)
    # Mapeia nomes de exibição/lógicos para nomes reais de colunas no DB se forem diferentes
    allowed_search_fields_map = {
        "Nome": "nome", "Sobrenome": "sobrenome", "CPF": "cpf", 
        "Email": "email", "Curso": "curso", "Cidade": "cidade", "UF": "uf"
    }
    # Colunas para ordenação (nomes reais do DB)
    allowed_sort_columns = ["id", "nome", "sobrenome", "telefone", "email", "cpf", 
                            "data_nascimento", "cidade", "uf", "curso"]

    params = []
    query = """
        SELECT id, nome, sobrenome, telefone, email, cpf, 
               DATE_FORMAT(data_nascimento, '%d/%m/%Y') as data_nascimento_formatada, 
               cidade, uf, curso 
        FROM alunos
    """

    # Adiciona cláusula WHERE para busca
    if search_field and search_term and search_field in allowed_search_fields_map:
        db_column_name = allowed_search_fields_map[search_field]
        query += f" WHERE {db_column_name} LIKE %s"
        params.append(f"%{search_term}%")
    
    # Adiciona cláusula ORDER BY para ordenação
    if sort_by_column and sort_by_column in allowed_sort_columns:
        # Valida a direção da ordenação
        if sort_direction.upper() not in ['ASC', 'DESC']:
            sort_direction = 'ASC' # Padrão seguro
        query += f" ORDER BY {sort_by_column} {sort_direction.upper()}"
    else:
        query += " ORDER BY nome ASC" # Ordenação padrão

    try:
        # print(f"SQL Executing: {query} with params {params}") # Para debug
        cursor.execute(query, tuple(params))
        resultados = cursor.fetchall()
        return resultados, f"{len(resultados)} alunos encontrados."
    except mysql.connector.Error as err:
        if err.errno == 1146: # Tabela não existe
             return None, f"Erro ao visualizar alunos: A tabela 'alunos' não existe no banco de dados '{db_config.DB_NAME}'."
        return None, f"Erro ao visualizar alunos: {err}"
    finally:
        if conexao and conexao.is_connected():
            cursor.close()
            conexao.close()

# --- Funções CRUD (cadastrar_aluno_db, atualizar_aluno_db, deletar_aluno_db) ---
# Estas funções permanecem como antes.
def cadastrar_aluno_db(dados_aluno):
    conexao = conectar_db()
    if not conexao:
        return False, "Falha na conexão com o banco de dados."
    cursor = conexao.cursor()
    sql = """
        INSERT INTO alunos (nome, sobrenome, telefone, email, cpf, data_nascimento, cidade, uf, curso)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(sql, dados_aluno)
        conexao.commit()
        return True, "Aluno cadastrado com sucesso!"
    except mysql.connector.Error as err:
        if err.errno == 1146:
             return False, f"Erro ao cadastrar aluno: A tabela 'alunos' não existe."
        if err.errno == 1062 and 'cpf' in err.msg.lower():
            return False, f"Erro ao cadastrar aluno: O CPF informado já existe."
        elif err.errno == 1062 and 'email' in err.msg.lower():
            return False, f"Erro ao cadastrar aluno: O Email informado já existe."
        return False, f"Erro ao cadastrar aluno: {err}"
    finally:
        if conexao and conexao.is_connected():
            cursor.close()
            conexao.close()

def atualizar_aluno_db(id_aluno, dados_aluno_atualizado):
    conexao = conectar_db()
    if not conexao:
        return False, "Falha na conexão com o banco de dados."
    cursor = conexao.cursor()
    sql = """
        UPDATE alunos
        SET nome = %s, sobrenome = %s, telefone = %s, email = %s,
            cpf = %s, data_nascimento = %s, cidade = %s, uf = %s, curso = %s
        WHERE id = %s
    """
    valores = dados_aluno_atualizado + (id_aluno,)
    try:
        cursor.execute(sql, valores)
        conexao.commit()
        return True, "Aluno atualizado com sucesso!"
    except mysql.connector.Error as err:
        if err.errno == 1146:
             return False, f"Erro ao atualizar aluno: A tabela 'alunos' não existe."
        if err.errno == 1062 and 'cpf' in err.msg.lower():
            return False, f"Erro ao atualizar aluno: O CPF informado já existe."
        elif err.errno == 1062 and 'email' in err.msg.lower():
            return False, f"Erro ao atualizar aluno: O Email informado já existe."
        return False, f"Erro ao atualizar aluno: {err}"
    finally:
        if conexao and conexao.is_connected():
            cursor.close()
            conexao.close()

def deletar_aluno_db(id_aluno):
    conexao = conectar_db()
    if not conexao:
        return False, "Falha na conexão com o banco de dados."
    cursor = conexao.cursor()
    sql = "DELETE FROM alunos WHERE id = %s"
    try:
        cursor.execute(sql, (id_aluno,))
        conexao.commit()
        return True, "Aluno deletado com sucesso!"
    except mysql.connector.Error as err:
        if err.errno == 1146:
             return False, f"Erro ao deletar aluno: A tabela 'alunos' não existe."
        return False, f"Erro ao deletar aluno: {err}"
    finally:
        if conexao and conexao.is_connected():
            cursor.close()
            conexao.close()