# utils/validators.py
import re
from datetime import date, datetime
from validate_docbr import CPF 
import logging
import os # Para ler variáveis de ambiente

logger = logging.getLogger(__name__) 

IDADE_MINIMA_ALUNO = 17

# --- Configuração da Validação de CPF Rigorosa ---
# Lê a configuração do arquivo .env. Se não estiver definida, assume True (validação rigorosa).
# Converte para booleano: 'true' (ignorando maiúsculas/minúsculas) será True, qualquer outra coisa False.
VALIDAR_CPF_RIGOROSAMENTE_STR = os.getenv('VALIDATE_CPF_STRICTLY', 'True')
VALIDAR_CPF_RIGOROSAMENTE = VALIDAR_CPF_RIGOROSAMENTE_STR.lower() == 'true'

if not VALIDAR_CPF_RIGOROSAMENTE:
    # Este log aparecerá uma vez quando o módulo for carregado, se a validação estiver desativada.
    logger.warning("*********************************************************************")
    logger.warning("* ATENÇÃO: A VALIDAÇÃO RIGOROSA DE DÍGITOS DO CPF ESTÁ DESATIVADA!  *")
    logger.warning("* CPFs fictícios que sigam o formato da máscara serão permitidos.   *")
    logger.warning("* Mude VALIDATE_CPF_STRICTLY para 'True' no arquivo .env para produção. *")
    logger.warning("*********************************************************************")


def validar_cpf_completo(cpf_string):
    """
    Valida um CPF. Se VALIDAR_CPF_RIGOROSAMENTE for True, usa validate-docbr.
    Caso contrário, permite o CPF se não estiver vazio (a máscara da GUI já cuidou do formato).
    Retorna (True, "") se válido, ou (False, "mensagem de erro") se inválido.
    """
    if not cpf_string: 
        return True, "" # CPF opcional, se vazio é considerado válido aqui

    if not VALIDAR_CPF_RIGOROSAMENTE:
        logger.info(f"Validação rigorosa de CPF desativada. Aceitando CPF '{cpf_string}' sem verificação de dígitos (modo de teste).")
        # A máscara da GUI (validar_formato_cpf em main_window.py) já deve ter garantido o formato ###.###.###-##.
        # Se você quisesse uma verificação de formato mínima aqui também, mesmo com a validação rigorosa desligada:
        # if not re.fullmatch(r"\d{3}\.\d{3}\.\d{3}-\d{2}", cpf_string):
        #     return False, "Formato de CPF inválido (mesmo com validação rigorosa desativada)."
        return True, "Validação de dígitos do CPF desativada (modo de teste)."

    # Validação rigorosa usando validate-docbr
    cpf_validator_obj = CPF()
    if cpf_validator_obj.validate(cpf_string):
        logger.debug(f"CPF '{cpf_string}' validado com sucesso (validate-docbr).")
        return True, ""
    else:
        logger.debug(f"Validação de CPF (validate-docbr) falhou para: '{cpf_string}'")
        return False, "CPF inválido (dígitos verificadores não conferem)."

# --- As outras funções de validação (email, telefone, data/idade) permanecem como antes ---
def validar_email_formato(email_string):
    if not email_string: return True, ""
    padrao_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(padrao_email, email_string): return True, ""
    else: logger.debug(f"Validação de formato de e-mail falhou para: '{email_string}'"); return False, "Formato de e-mail inválido."

def validar_telefone_formato(telefone_string):
    if not telefone_string: return True, ""
    telefone_limpo = telefone_string.strip()
    padrao_telefone = r"^\(\d{2}\) (?:9\d{4}-\d{4}|\d{4}-\d{4})$"
    if re.fullmatch(padrao_telefone, telefone_limpo): return True, ""
    else: logger.debug(f"Validação de formato de telefone falhou para: '{telefone_string}'"); return False, "Formato de telefone inválido. Use (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."

def validar_data_nascimento_e_idade(data_nasc_str_yyyy_mm_dd):
    if not data_nasc_str_yyyy_mm_dd: return True, "" 
    try:
        data_nasc = datetime.strptime(data_nasc_str_yyyy_mm_dd, '%Y-%m-%d').date()
    except ValueError as e:
        logger.warning(f"Formato de data inválido para validação de idade: '{data_nasc_str_yyyy_mm_dd}'. Erro: {e}")
        return False, "Formato de data de nascimento inválido para backend (esperado<y_bin_46>-MM-DD)."
    hoje = date.today()
    if data_nasc > hoje:
        logger.warning(f"Tentativa de usar data de nascimento futura: {data_nasc}")
        return False, "Data de nascimento não pode ser uma data futura."
    idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
    logger.debug(f"[Validador Idade] Data Nasc: {data_nasc}, Hoje: {hoje}, Idade Calculada: {idade}, Mínima: {IDADE_MINIMA_ALUNO}")
    if idade < IDADE_MINIMA_ALUNO:
        logger.info(f"Validação de idade falhou: Aluno com {idade} anos (mínimo {IDADE_MINIMA_ALUNO}). Data Nasc: {data_nasc_str_yyyy_mm_dd}")
        return False, f"O aluno deve ter pelo menos {IDADE_MINIMA_ALUNO} anos. Idade atual: {idade}."
    return True, ""