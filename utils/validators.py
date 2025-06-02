# utils/validators.py
import re
from datetime import date, datetime
from validate_docbr import CPF 
import logging
import os

logger = logging.getLogger(__name__)

# --- Constantes ---
IDADE_MINIMA_ALUNO = 17

# --- Configuração da Validação de CPF ---
# Lê a flag do .env. Assume validação rigorosa (True) se não definida ou se o valor não for 'false'.
VALIDAR_CPF_RIGOROSAMENTE_STR = os.getenv('VALIDATE_CPF_STRICTLY', 'True')
VALIDAR_CPF_RIGOROSAMENTE = VALIDAR_CPF_RIGOROSAMENTE_STR.lower() == 'true'

if not VALIDAR_CPF_RIGOROSAMENTE:
    logger.warning("Validação rigorosa de dígitos do CPF DESATIVADA (VALIDATE_CPF_STRICTLY=False).")

def validar_cpf_completo(cpf_string):
    """
    Valida um CPF. Verifica o formato da máscara e, se VALIDAR_CPF_RIGOROSAMENTE for True,
    usa validate-docbr para verificar os dígitos.
    Retorna (True, "") se válido, ou (False, "mensagem de erro") se inválido.
    """
    if not cpf_string: 
        return True, "" # Considera CPF vazio como válido (opcional)

    # Validação do formato da máscara (###.###.###-##)
    if not re.fullmatch(r"\d{3}\.\d{3}\.\d{3}-\d{2}", cpf_string):
        logger.debug(f"Formato de máscara do CPF '{cpf_string}' é inválido.")
        return False, "CPF: Formato inválido (esperado ###.###.###-##)."

    if not VALIDAR_CPF_RIGOROSAMENTE:
        logger.info(f"Validação de dígitos do CPF desativada. CPF '{cpf_string}' aceito (formato máscara OK).")
        return True, "Validação de dígitos do CPF desativada (modo de teste)."

    # Validação rigorosa dos dígitos com validate-docbr
    cpf_validator_obj = CPF()
    if cpf_validator_obj.validate(cpf_string):
        logger.debug(f"CPF '{cpf_string}' validado com sucesso (validate-docbr).")
        return True, ""
    else:
        logger.debug(f"Validação de dígitos do CPF (validate-docbr) falhou para: '{cpf_string}'")
        return False, "CPF inválido (dígitos verificadores não conferem)."

def validar_email_formato(email_string):
    """Valida o formato básico de um endereço de e-mail."""
    if not email_string: return True, "" 
    
    # Regex padrão para formatos comuns de email
    padrao_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(padrao_email, email_string): 
        return True, ""
    else: 
        logger.debug(f"Formato de e-mail inválido: '{email_string}'")
        return False, "E-mail: Formato inválido."

def validar_telefone_formato(telefone_string):
    """Valida o formato do telefone para (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."""
    if not telefone_string: return True, ""
        
    telefone_limpo = telefone_string.strip()
    # Aceita celular com 9 dígitos ou fixo com 8 dígitos após o DDD
    padrao_telefone = r"^\(\d{2}\) (?:9\d{4}-\d{4}|\d{4}-\d{4})$" 
    
    if re.fullmatch(padrao_telefone, telefone_limpo):
        return True, ""
    else:
        logger.debug(f"Formato de telefone inválido: '{telefone_string}'")
        return False, "Telefone: Formato inválido. Use (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."

def validar_data_nascimento_e_idade(data_nasc_str_yyyy_mm_dd):
    """
    Valida se a data de nascimento é uma data real (formato YYYY-MM-DD),
    não é futura, e se o aluno atende à idade mínima.
    """
    if not data_nasc_str_yyyy_mm_dd: return True, "" 

    try:
        data_nasc = datetime.strptime(data_nasc_str_yyyy_mm_dd, '%Y-%m-%d').date()
    except ValueError: # Erro na conversão da string para data
        logger.warning(f"Data Nasc.: Formato inválido para backend ('{data_nasc_str_yyyy_mm_dd}'), esperado YYYY-MM-DD.")
        return False, "Data Nasc.: Formato inválido para processamento."

    hoje = date.today()
    if data_nasc > hoje: # Data de nascimento não pode ser no futuro
        logger.warning(f"Data de nascimento futura informada: {data_nasc}")
        return False, "Data de nascimento não pode ser uma data futura."

    # Cálculo preciso da idade
    idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
    logger.debug(f"Validação de Idade: DataNasc='{data_nasc}', Hoje='{hoje}', IdadeCalc='{idade}', Mínima='{IDADE_MINIMA_ALUNO}'")

    if idade < IDADE_MINIMA_ALUNO:
        logger.info(f"Validação de idade falhou: Aluno com {idade} anos (mínimo {IDADE_MINIMA_ALUNO}). Data Nasc: {data_nasc_str_yyyy_mm_dd}")
        return False, f"Aluno deve ter pelo menos {IDADE_MINIMA_ALUNO} anos. Idade calculada: {idade}."
        
    return True, ""