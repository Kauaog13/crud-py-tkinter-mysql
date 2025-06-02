import os
from dotenv import load_dotenv
from tkinter import messagebox 

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"Arquivo .env carregado de: {dotenv_path}")
else:
    print(f"AVISO: Arquivo .env não encontrado em {dotenv_path}. Usando variáveis de ambiente existentes ou valores padrão (se houver).")
  
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "facsenac")

print(f"Configurações do DB carregadas: HOST={DB_HOST}, USER={DB_USER}, NAME={DB_NAME}, PASSWORD_SET={'Sim' if DB_PASSWORD else 'Não'}")