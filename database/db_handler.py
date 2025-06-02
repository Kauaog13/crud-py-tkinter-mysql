# database/db_handler.py
import mysql.connector
from . import db_config # Importa db_config do mesmo pacote 'database'
from utils import validators 
import logging

logger = logging.getLogger(__name__)

def conectar_db():
    try:
        conexao = mysql.connector.connect(
            host=db_config.DB_HOST, user=db_config.DB_USER,
            password=db_config.DB_PASSWORD, database=db_config.DB_NAME
        )
        logger.debug(f"Conexão com BD ({db_config.DB_NAME}@{db_config.DB_HOST}) estabelecida.")
        return conexao
    except mysql.connector.Error as err:
        logger.error(f"Falha ao conectar ao BD ({db_config.DB_NAME}@{db_config.DB_HOST}): {err}", exc_info=False)
        return None

def _validar_dados_aluno(nome, sobrenome, telefone, email, cpf, data_nascimento_str_yyyy_mm_dd):
    """Função auxiliar para validar os dados do aluno antes de inserir/atualizar no backend."""
    logger.debug(f"Backend validando dados: CPF='{cpf}', Email='{email}', Tel='{telefone}', DataNasc='{data_nascimento_str_yyyy_mm_dd}'")
    
    # Validações de formato e regras de negócio
    valido, msg = validators.validar_cpf_completo(cpf)
    if not valido: logger.warning(f"Validação de CPF falhou (backend): {msg}"); return False, msg
    
    valido, msg = validators.validar_email_formato(email)
    if not valido: logger.warning(f"Validação de Email falhou (backend): {msg}"); return False, msg
    
    valido, msg = validators.validar_telefone_formato(telefone)
    if not valido: logger.warning(f"Validação de Telefone falhou (backend): {msg}"); return False, msg
    
    # data_nascimento_str_yyyy_mm_dd já está no formato YYYY-MM-DD ou None
    valido, msg = validators.validar_data_nascimento_e_idade(data_nascimento_str_yyyy_mm_dd)
    if not valido: logger.warning(f"Validação de Data Nasc/Idade falhou (backend): {msg}"); return False, msg
    
    logger.debug("Todas as validações de backend passaram para os dados fornecidos.")
    return True, ""

def cadastrar_aluno_db(dados_aluno):
    # dados_aluno = (nome, sobrenome, telefone, email, cpf, data_nasc_db_format, cidade, uf, curso)
    nome, sobrenome, telefone, email, cpf, data_nasc_db_format, cidade, uf, curso = dados_aluno
    logger.info(f"Tentando cadastrar aluno: {nome} {sobrenome}, CPF: {cpf}")
    
    valido, msg_validacao = _validar_dados_aluno(nome, sobrenome, telefone, email, cpf, data_nasc_db_format)
    if not valido:
        logger.warning(f"Validação de backend falhou para cadastro de '{nome} {sobrenome}': {msg_validacao}")
        return False, msg_validacao

    conexao = conectar_db()
    if not conexao: return False, "Falha na conexão com o banco de dados."
    cursor = conexao.cursor()
    sql = """
        INSERT INTO alunos (nome, sobrenome, telefone, email, cpf, data_nascimento, cidade, uf, curso)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(sql, dados_aluno)
        conexao.commit()
        logger.info(f"Aluno '{nome} {sobrenome}' (ID: {cursor.lastrowid}) cadastrado com sucesso no BD.")
        return True, "Aluno cadastrado com sucesso!"
    except mysql.connector.Error as err:
        logger.error(f"Erro SQL ao cadastrar aluno '{nome} {sobrenome}': {err}", exc_info=True)
        if err.errno == 1146: return False, "Erro: Tabela 'alunos' não existe."
        if err.errno == 1062: # Erro de entrada duplicada (UNIQUE constraint)
            if 'cpf' in err.msg.lower(): return False, "Erro: CPF já cadastrado."
            elif 'email' in err.msg.lower(): return False, "Erro: Email já cadastrado."
            else: return False, f"Erro: Violação de campo único - {err.msg}"
        return False, f"Erro ao cadastrar aluno no BD: {err.msg}"
    finally:
        if conexao and conexao.is_connected(): cursor.close(); conexao.close()

def atualizar_aluno_db(id_aluno, dados_aluno_atualizado):
    nome, sobrenome, telefone, email, cpf, data_nasc_db_format, _, _, _ = dados_aluno_atualizado
    logger.info(f"Tentando atualizar aluno ID: {id_aluno} - {nome} {sobrenome}")

    valido, msg_validacao = _validar_dados_aluno(nome, sobrenome, telefone, email, cpf, data_nasc_db_format)
    if not valido:
        logger.warning(f"Validação de backend falhou para atualização do aluno ID {id_aluno}: {msg_validacao}")
        return False, msg_validacao

    conexao = conectar_db()
    if not conexao: return False, "Falha na conexão com o banco de dados."
    cursor = conexao.cursor()
    sql = """
        UPDATE alunos SET nome = %s, sobrenome = %s, telefone = %s, email = %s,
            cpf = %s, data_nascimento = %s, cidade = %s, uf = %s, curso = %s
        WHERE id = %s
    """
    valores = dados_aluno_atualizado + (id_aluno,)
    try:
        cursor.execute(sql, valores)
        conexao.commit()
        if cursor.rowcount == 0:
            logger.warning(f"Nenhum aluno encontrado com ID {id_aluno} para atualização.")
            return False, "Nenhum aluno encontrado com o ID fornecido para atualização."
        logger.info(f"Aluno ID {id_aluno} atualizado com sucesso no BD.")
        return True, "Aluno atualizado com sucesso!"
    except mysql.connector.Error as err:
        logger.error(f"Erro SQL ao atualizar aluno ID {id_aluno}: {err}", exc_info=True)
        if err.errno == 1146: return False, "Erro: Tabela 'alunos' não existe."
        if err.errno == 1062:
            if 'cpf' in err.msg.lower(): return False, "Erro: CPF já cadastrado para outro aluno."
            elif 'email' in err.msg.lower(): return False, "Erro: Email já cadastrado para outro aluno."
            else: return False, f"Erro: Violação de campo único - {err.msg}"
        return False, f"Erro ao atualizar aluno no BD: {err.msg}"
    finally:
        if conexao and conexao.is_connected(): cursor.close(); conexao.close()

def visualizar_alunos_db(search_field=None, search_term=None, sort_by_column=None, sort_direction='ASC'):
    logger.debug(f"Visualizando alunos: busca='{search_field}':'{search_term}', ordenar='{sort_by_column}':'{sort_direction}'")
    conexao = conectar_db()
    if not conexao: return None, "Falha na conexão com o banco de dados."
    cursor = conexao.cursor()
    allowed_search_fields_map = {"Nome": "nome", "Sobrenome": "sobrenome", "CPF": "cpf", "Email": "email", "Curso": "curso", "Cidade": "cidade", "UF": "uf"}
    allowed_sort_columns = ["id", "nome", "sobrenome", "telefone", "email", "cpf", "data_nascimento", "cidade", "uf", "curso"]
    params = []
    query = "SELECT id, nome, sobrenome, telefone, email, cpf, DATE_FORMAT(data_nascimento, '%d/%m/%Y') as data_nascimento_formatada, cidade, uf, curso FROM alunos"
    if search_field and search_term and search_field in allowed_search_fields_map:
        db_column_name = allowed_search_fields_map[search_field]
        query += f" WHERE {db_column_name} LIKE %s"
        params.append(f"%{search_term}%")
    if sort_by_column and sort_by_column in allowed_sort_columns:
        if sort_direction.upper() not in ['ASC', 'DESC']: sort_direction = 'ASC'
        query += f" ORDER BY {sort_by_column} {sort_direction.upper()}"
    else: query += " ORDER BY nome ASC"
    try:
        logger.debug(f"Executando SQL: {query} com params: {params}")
        cursor.execute(query, tuple(params))
        resultados = cursor.fetchall()
        logger.info(f"{len(resultados)} alunos encontrados e retornados da visualização.")
        return resultados, f"{len(resultados)} alunos encontrados."
    except mysql.connector.Error as err:
        logger.error(f"Erro SQL ao visualizar alunos: {err}", exc_info=True)
        if err.errno == 1146: return None, "Erro: Tabela 'alunos' não existe."
        return None, f"Erro ao visualizar alunos: {err.msg}"
    finally:
        if conexao and conexao.is_connected(): cursor.close(); conexao.close()

def deletar_aluno_db(id_aluno):
    logger.info(f"Tentando deletar aluno ID: {id_aluno}")
    conexao = conectar_db()
    if not conexao: return False, "Falha na conexão com o banco de dados."
    cursor = conexao.cursor()
    sql = "DELETE FROM alunos WHERE id = %s"
    try:
        cursor.execute(sql, (id_aluno,))
        conexao.commit()
        if cursor.rowcount == 0:
            logger.warning(f"Nenhum aluno encontrado com ID {id_aluno} para deleção.")
            return False, "Nenhum aluno encontrado com o ID fornecido para deleção."
        logger.info(f"Aluno ID {id_aluno} deletado com sucesso do BD.")
        return True, "Aluno deletado com sucesso!"
    except mysql.connector.Error as err:
        logger.error(f"Erro SQL ao deletar aluno ID {id_aluno}: {err}", exc_info=True)
        if err.errno == 1146: return False, "Erro: Tabela 'alunos' não existe."
        return False, f"Erro ao deletar aluno no BD: {err.msg}"
    finally:
        if conexao and conexao.is_connected(): cursor.close(); conexao.close()