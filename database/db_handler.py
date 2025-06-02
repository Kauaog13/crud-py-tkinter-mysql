# database/db_handler.py
import mysql.connector
from . import db_config
from utils import validators # Importa os validadores

def conectar_db():
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

def _validar_dados_aluno(nome, sobrenome, telefone, email, cpf, data_nascimento_str_yyyy_mm_dd):
    # Nome e Sobrenome são validados como obrigatórios na GUI.
    # Aqui focamos em formatos e regras de negócio.
    
    valido, msg = validators.validar_cpf_completo(cpf)
    if not valido: return False, msg
    
    valido, msg = validators.validar_email_formato(email)
    if not valido: return False, msg
    
    valido, msg = validators.validar_telefone_formato(telefone)
    if not valido: return False, msg
    
    # DEBUG: Imprime dados antes de validar idade no backend
    print(f"[Backend Validar] Validando idade para data (YYYY-MM-DD): {data_nascimento_str_yyyy_mm_dd}")
    valido, msg = validators.validar_data_nascimento_e_idade(data_nascimento_str_yyyy_mm_dd)
    if not valido: return False, msg
    
    return True, ""

def cadastrar_aluno_db(dados_aluno):
    nome, sobrenome, telefone, email, cpf, data_nasc_db_format, cidade, uf, curso = dados_aluno
    
    valido, msg_validacao = _validar_dados_aluno(nome, sobrenome, telefone, email, cpf, data_nasc_db_format)
    if not valido:
        return False, msg_validacao

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
             return False, f"Erro ao cadastrar: Tabela 'alunos' não existe."
        if err.errno == 1062:
            if 'cpf' in err.msg.lower(): return False, "Erro: CPF já cadastrado."
            elif 'email' in err.msg.lower(): return False, "Erro: Email já cadastrado."
            else: return False, f"Erro: Violação de campo único. {err.msg}"
        return False, f"Erro ao cadastrar aluno no BD: {err}"
    finally:
        if conexao and conexao.is_connected():
            cursor.close(); conexao.close()

def atualizar_aluno_db(id_aluno, dados_aluno_atualizado):
    nome, sobrenome, telefone, email, cpf, data_nasc_db_format, cidade, uf, curso = dados_aluno_atualizado

    valido, msg_validacao = _validar_dados_aluno(nome, sobrenome, telefone, email, cpf, data_nasc_db_format)
    if not valido:
        return False, msg_validacao

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
        if cursor.rowcount == 0:
            return False, "Nenhum aluno encontrado com o ID para atualização."
        return True, "Aluno atualizado com sucesso!"
    except mysql.connector.Error as err:
        if err.errno == 1146:
             return False, f"Erro ao atualizar: Tabela 'alunos' não existe."
        if err.errno == 1062:
            if 'cpf' in err.msg.lower(): return False, "Erro: CPF já cadastrado para outro aluno."
            elif 'email' in err.msg.lower(): return False, "Erro: Email já cadastrado para outro aluno."
            else: return False, f"Erro: Violação de campo único. {err.msg}"
        return False, f"Erro ao atualizar aluno no BD: {err}"
    finally:
        if conexao and conexao.is_connected():
            cursor.close(); conexao.close()

def visualizar_alunos_db(search_field=None, search_term=None, sort_by_column=None, sort_direction='ASC'):
    conexao = conectar_db()
    if not conexao: return None, "Falha na conexão com o banco de dados."
    cursor = conexao.cursor()
    allowed_search_fields_map = {
        "Nome": "nome", "Sobrenome": "sobrenome", "CPF": "cpf", 
        "Email": "email", "Curso": "curso", "Cidade": "cidade", "UF": "uf"
    }
    allowed_sort_columns = ["id", "nome", "sobrenome", "telefone", "email", "cpf", 
                            "data_nascimento", "cidade", "uf", "curso"]
    params = []
    query = "SELECT id, nome, sobrenome, telefone, email, cpf, DATE_FORMAT(data_nascimento, '%d/%m/%Y') as data_nascimento_formatada, cidade, uf, curso FROM alunos"
    
    if search_field and search_term and search_field in allowed_search_fields_map:
        db_column_name = allowed_search_fields_map[search_field]
        query += f" WHERE {db_column_name} LIKE %s"
        params.append(f"%{search_term}%")
    
    if sort_by_column and sort_by_column in allowed_sort_columns:
        if sort_direction.upper() not in ['ASC', 'DESC']: sort_direction = 'ASC'
        query += f" ORDER BY {sort_by_column} {sort_direction.upper()}"
    else:
        query += " ORDER BY nome ASC"
    
    try:
        cursor.execute(query, tuple(params))
        resultados = cursor.fetchall()
        return resultados, f"{len(resultados)} alunos encontrados."
    except mysql.connector.Error as err:
        if err.errno == 1146: return None, f"Erro: Tabela 'alunos' não existe."
        return None, f"Erro ao visualizar alunos: {err}"
    finally:
        if conexao and conexao.is_connected():
            cursor.close(); conexao.close()

def deletar_aluno_db(id_aluno):
    conexao = conectar_db()
    if not conexao: return False, "Falha na conexão com o banco de dados."
    cursor = conexao.cursor()
    sql = "DELETE FROM alunos WHERE id = %s"
    try:
        cursor.execute(sql, (id_aluno,))
        conexao.commit()
        if cursor.rowcount == 0:
             return False, "Nenhum aluno encontrado com o ID para deleção."
        return True, "Aluno deletado com sucesso!"
    except mysql.connector.Error as err:
        if err.errno == 1146: return False, f"Erro: Tabela 'alunos' não existe."
        return False, f"Erro ao deletar aluno no BD: {err}"
    finally:
        if conexao and conexao.is_connected():
            cursor.close(); conexao.close()