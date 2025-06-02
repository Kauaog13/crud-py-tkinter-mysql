# database/db_handler.py
import mysql.connector
from . import db_config 
from utils import validators 
import logging

logger = logging.getLogger(__name__)

def conectar_db():
    """Estabelece conexão com o banco de dados MySQL."""
    try:
        conexao = mysql.connector.connect(
            host=db_config.DB_HOST, user=db_config.DB_USER,
            password=db_config.DB_PASSWORD, database=db_config.DB_NAME
        )
        logger.debug(f"Conexão com BD ({db_config.DB_NAME}@{db_config.DB_HOST}) estabelecida.")
        return conexao
    except mysql.connector.Error as err:
        # Loga o erro detalhado, incluindo traceback se útil, mas retorna None para a chamada.
        # A GUI ou o chamador de mais alto nível deve lidar com a ausência de conexão.
        logger.error(f"Falha ao conectar ao BD ({db_config.DB_NAME}@{db_config.DB_HOST}): {err}", exc_info=False) 
        return None

def _validar_dados_aluno_backend(dados_aluno_desempacotados):
    """Valida os dados do aluno no backend antes de operações DB."""
    nome, sobrenome, telefone, email, cpf, data_nasc_db_format, _, _, _ = dados_aluno_desempacotados
    logger.debug(f"Backend validando dados para '{nome} {sobrenome}': CPF='{cpf}', Email='{email}', Tel='{telefone}', DataNasc='{data_nasc_db_format}'")
    
    validacoes = [
        validators.validar_cpf_completo(cpf),
        validators.validar_email_formato(email),
        validators.validar_telefone_formato(telefone),
        validators.validar_data_nascimento_e_idade(data_nasc_db_format)
    ]
    
    for valido, msg in validacoes:
        if not valido:
            logger.warning(f"Validação de backend falhou: {msg}")
            return False, msg # Retorna a primeira falha de validação
    
    logger.debug("Todas as validações de backend passaram.")
    return True, ""

def cadastrar_aluno_db(dados_aluno):
    """Cadastra um novo aluno após validação no backend."""
    # dados_aluno = (nome, sobrenome, telefone, email, cpf, data_nasc_db_format, cidade, uf, curso)
    logger.info(f"Tentando cadastrar aluno: {dados_aluno[0]} {dados_aluno[1]}")
    
    valido, msg_validacao = _validar_dados_aluno_backend(dados_aluno)
    if not valido:
        return False, msg_validacao # Retorna mensagem da validação que falhou

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
        aluno_id = cursor.lastrowid
        logger.info(f"Aluno '{dados_aluno[0]} {dados_aluno[1]}' (ID: {aluno_id}) cadastrado com sucesso.")
        return True, "Aluno cadastrado com sucesso!"
    except mysql.connector.Error as err:
        logger.error(f"Erro SQL ao cadastrar aluno '{dados_aluno[0]}': {err}", exc_info=True)
        if err.errno == 1146: return False, "Erro: Tabela 'alunos' não existe."
        if err.errno == 1062: # Violação de chave única
            if 'cpf' in err.msg.lower(): return False, "Erro: CPF já cadastrado."
            elif 'email' in err.msg.lower(): return False, "Erro: Email já cadastrado."
            return False, f"Erro: Dados duplicados não permitidos ({err.msg})."
        return False, f"Erro no BD ao cadastrar: {err.msg}" # Mensagem mais curta para GUI
    finally:
        if conexao and conexao.is_connected(): cursor.close(); conexao.close()

def atualizar_aluno_db(id_aluno, dados_aluno_atualizado):
    """Atualiza dados de um aluno existente após validação no backend."""
    logger.info(f"Tentando atualizar aluno ID: {id_aluno}")

    valido, msg_validacao = _validar_dados_aluno_backend(dados_aluno_atualizado)
    if not valido:
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
            logger.warning(f"Nenhum aluno encontrado com ID {id_aluno} para atualização (ou dados eram iguais).")
            # Considerar se isso é um erro ou um "nada a fazer"
            return False, "Nenhum aluno encontrado com o ID para atualizar ou dados idênticos."
        logger.info(f"Aluno ID {id_aluno} atualizado com sucesso.")
        return True, "Aluno atualizado com sucesso!"
    except mysql.connector.Error as err:
        logger.error(f"Erro SQL ao atualizar aluno ID {id_aluno}: {err}", exc_info=True)
        if err.errno == 1146: return False, "Erro: Tabela 'alunos' não existe."
        if err.errno == 1062:
            if 'cpf' in err.msg.lower(): return False, "Erro: CPF já pertence a outro aluno."
            elif 'email' in err.msg.lower(): return False, "Erro: Email já pertence a outro aluno."
            return False, f"Erro: Dados duplicados não permitidos ({err.msg})."
        return False, f"Erro no BD ao atualizar: {err.msg}"
    finally:
        if conexao and conexao.is_connected(): cursor.close(); conexao.close()

def visualizar_alunos_db(search_field=None, search_term=None, sort_by_column=None, sort_direction='ASC'):
    """Busca alunos no BD com opções de filtro e ordenação."""
    logger.debug(f"Buscando alunos: filtro='{search_field}':'{search_term}', ordem='{sort_by_column} {sort_direction}'")
    conexao = conectar_db()
    if not conexao: return None, "Falha na conexão com o banco de dados."
    
    cursor = conexao.cursor()
    # Mapeamento seguro de campos de busca para colunas do DB
    allowed_search_fields_map = {
        "Nome": "nome", "Sobrenome": "sobrenome", "CPF": "cpf", 
        "Email": "email", "Curso": "curso", "Cidade": "cidade", "UF": "uf"
    }
    # Colunas permitidas para ordenação (nomes reais do DB)
    allowed_sort_columns = ["id", "nome", "sobrenome", "telefone", "email", "cpf", 
                            "data_nascimento", "cidade", "uf", "curso"]
    params = []
    # Query base com data formatada para exibição
    query = """
        SELECT id, nome, sobrenome, telefone, email, cpf, 
               DATE_FORMAT(data_nascimento, '%d/%m/%Y') as data_nascimento_formatada, 
               cidade, uf, curso 
        FROM alunos
    """
    
    # Adiciona filtro WHERE se aplicável
    if search_field and search_term and search_field in allowed_search_fields_map:
        db_column_name = allowed_search_fields_map[search_field]
        query += f" WHERE {db_column_name} LIKE %s" # Usa LIKE para busca parcial
        params.append(f"%{search_term}%") # Adiciona % para o LIKE
    
    # Adiciona ordenação ORDER BY se aplicável
    if sort_by_column and sort_by_column in allowed_sort_columns:
        # Valida direção da ordenação
        sort_direction_safe = 'ASC' if sort_direction.upper() == 'ASC' else 'DESC'
        query += f" ORDER BY {sort_by_column} {sort_direction_safe}"
    else:
        query += " ORDER BY nome ASC" # Ordenação padrão se nenhuma for especificada
    
    try:
        logger.debug(f"Executando SQL: {query} com params: {params}")
        cursor.execute(query, tuple(params))
        resultados = cursor.fetchall()
        msg = f"{len(resultados)} aluno(s) encontrado(s)."
        logger.info(msg)
        return resultados, msg
    except mysql.connector.Error as err:
        logger.error(f"Erro SQL ao visualizar alunos: {err}", exc_info=True)
        if err.errno == 1146: return None, "Erro: Tabela 'alunos' não existe." # Tabela não existe
        return None, f"Erro ao visualizar alunos: {err.msg}"
    finally:
        if conexao and conexao.is_connected(): cursor.close(); conexao.close()

def deletar_aluno_db(id_aluno):
    """Deleta um aluno do banco de dados pelo ID."""
    logger.info(f"Tentando deletar aluno ID: {id_aluno}")
    conexao = conectar_db()
    if not conexao: return False, "Falha na conexão com o banco de dados."
    
    cursor = conexao.cursor()
    sql = "DELETE FROM alunos WHERE id = %s"
    try:
        cursor.execute(sql, (id_aluno,))
        conexao.commit()
        if cursor.rowcount == 0: # Verifica se alguma linha foi realmente deletada
            logger.warning(f"Nenhum aluno encontrado com ID {id_aluno} para deleção.")
            return False, "Nenhum aluno encontrado com o ID fornecido para deleção."
        logger.info(f"Aluno ID {id_aluno} deletado com sucesso do BD.")
        return True, "Aluno deletado com sucesso!"
    except mysql.connector.Error as err:
        logger.error(f"Erro SQL ao deletar aluno ID {id_aluno}: {err}", exc_info=True)
        if err.errno == 1146: return False, "Erro: Tabela 'alunos' não existe."
        return False, f"Erro no BD ao deletar: {err.msg}"
    finally:
        if conexao and conexao.is_connected(): cursor.close(); conexao.close()