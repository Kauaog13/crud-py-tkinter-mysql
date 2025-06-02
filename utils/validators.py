# utils/validators.py
import re
from datetime import date, datetime
from validate_docbr import CPF # Usando validate-docbr

IDADE_MINIMA_ALUNO = 17 # Constante para a idade mínima

def validar_cpf_completo(cpf_string):
    """
    Valida um CPF usando a biblioteca validate-docbr.
    Retorna (True, "") se válido, ou (False, "mensagem de erro") se inválido.
    """
    if not cpf_string: 
        return True, "" # CPF opcional, se vazio é considerado válido aqui
    
    cpf_validator_obj = CPF()
    if cpf_validator_obj.validate(cpf_string):
        return True, ""
    else:
        return False, "CPF inválido."

def validar_email_formato(email_string):
    """
    Valida o formato do email usando uma expressão regular.
    Retorna (True, "") se válido, ou (False, "mensagem de erro") se inválido.
    """
    if not email_string:
        return True, "" # Email opcional
    
    padrao_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(padrao_email, email_string):
        return True, ""
    else:
        return False, "Formato de e-mail inválido."

def validar_telefone_formato(telefone_string):
    """
    Valida o formato do telefone para (XX) XXXXX-XXXX ou (XX) XXXX-XXXX.
    Retorna (True, "") se válido, ou (False, "mensagem de erro") se inválido.
    """
    if not telefone_string:
        return True, "" # Telefone opcional
        
    telefone_limpo = telefone_string.strip()
    padrao_telefone = r"^\(\d{2}\) (?:9\d{4}-\d{4}|\d{4}-\d{4})$"
    
    if re.fullmatch(padrao_telefone, telefone_limpo):
        return True, ""
    else:
        return False, "Formato de telefone inválido. Use (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."

def validar_data_nascimento_e_idade(data_nasc_str_yyyy_mm_dd):
    """
    Valida se a data de nascimento é uma data válida e se o aluno tem a idade mínima.
    Espera a data como string no formato 'YYYY-MM-DD'.
    Retorna (True, "") se válido, ou (False, "mensagem de erro") se inválido.
    """
    if not data_nasc_str_yyyy_mm_dd:
        return True, "" # Data de nascimento opcional, passa se vazia

    try:
        data_nasc = datetime.strptime(data_nasc_str_yyyy_mm_dd, '%Y-%m-%d').date()
    except ValueError:
        return False, "Formato de data de nascimento inválido para backend (esperado YYYY-MM-DD)."

    hoje = date.today()
    
    if data_nasc > hoje:
        return False, "Data de nascimento não pode ser uma data futura."

    idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
    
    # DEBUG: Imprime informações para depuração da idade
    print(f"[Validador Idade] Data Nasc: {data_nasc}, Hoje: {hoje}, Idade Calculada: {idade}, Mínima: {IDADE_MINIMA_ALUNO}")

    if idade < IDADE_MINIMA_ALUNO:
        return False, f"O aluno deve ter pelo menos {IDADE_MINIMA_ALUNO} anos. Idade atual: {idade}."
        
    return True, ""