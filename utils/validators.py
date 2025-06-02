import re

def validar_email(email):
    """Valida um formato de email simples."""
    if not email:
        return True
    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(padrao, email) is not None

def validar_telefone(telefone):
    """Valida um formato de telefone (apenas números, opcionalmente com parênteses e hífen)."""
    if not telefone: 
        return True
    padrao = r"^\(?[1-9]{2}\)? ?(?:[2-8]|9[1-9])[0-9]{3}-?[0-9]{4}$"
    return re.match(padrao, telefone) is not None

