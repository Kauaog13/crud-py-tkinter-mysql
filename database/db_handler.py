# database/db_handler.py
import mysql.connector
from tkinter import messagebox
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
             return False, f"Erro ao cadastrar aluno: A tabela 'alunos' não existe no banco de dados '{db_config.DB_NAME}'. Verifique a configuração."
        if err.errno == 1062 and 'cpf' in err.msg.lower():
            return False, f"Erro ao cadastrar aluno: O CPF informado já existe."
        return False, f"Erro ao cadastrar aluno: {err}"
    finally:
        if conexao and conexao.is_connected():
            cursor.close()
            conexao.close()

def visualizar_alunos_db():
    conexao = conectar_db()
    if not conexao:
        return None, "Falha na conexão com o banco de dados."
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id, nome, sobrenome, telefone, email, cpf, DATE_FORMAT(data_nascimento, '%d/%m/%Y') as data_nascimento_formatada, cidade, uf, curso FROM alunos ORDER BY nome")
        resultados = cursor.fetchall()
        return resultados, "Alunos listados com sucesso."
    except mysql.connector.Error as err:
        if err.errno == 1146:
             return None, f"Erro ao visualizar alunos: A tabela 'alunos' não existe no banco de dados '{db_config.DB_NAME}'. Verifique a configuração."
        return None, f"Erro ao visualizar alunos: {err}"
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
             return False, f"Erro ao atualizar aluno: A tabela 'alunos' não existe no banco de dados '{db_config.DB_NAME}'. Verifique a configuração."
        if err.errno == 1062 and 'cpf' in err.msg.lower():
            return False, f"Erro ao atualizar aluno: O CPF informado já existe."
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
             return False, f"Erro ao deletar aluno: A tabela 'alunos' não existe no banco de dados '{db_config.DB_NAME}'. Verifique a configuração."
        return False, f"Erro ao deletar aluno: {err}"
    finally:
        if conexao and conexao.is_connected():
            cursor.close()
            conexao.close()