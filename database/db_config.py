# database/db_config.py
import os
from dotenv import load_dotenv
import logging # Adicionado para logging

# Configura um logger específico para este módulo, se não configurado no app_alunos.py antes da importação.
# No entanto, é melhor que a configuração principal do logging seja feita em app_alunos.py.
# Aqui, apenas obtemos o logger.
logger = logging.getLogger(__name__)

# Constrói o caminho para o arquivo .env na raiz do projeto
# __file__ é o caminho para db_config.py
# os.path.dirname(__file__) é o diretório 'database'
# os.path.dirname(os.path.dirname(__file__)) é a raiz do projeto
DOTENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

if os.path.exists(DOTENV_PATH):
    load_dotenv(DOTENV_PATH)
    # Usar logger.info em vez de print
    logger.info(f"Arquivo .env carregado de: {DOTENV_PATH}")
else:
    logger.warning(f"Arquivo .env não encontrado em {DOTENV_PATH}. Usando variáveis de ambiente ou padrões.")

# Lê as variáveis de ambiente ou usa valores padrão
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER") # Sem padrão para usuário e senha, para forçar configuração
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "facsenac")

# Loga as configurações carregadas (sem a senha)
logger.info(f"Configurações do DB: HOST={DB_HOST}, USER={DB_USER}, NAME={DB_NAME}, PASSWORD_SET={'Sim' if DB_PASSWORD else 'Não'}")

# Verifica se as credenciais essenciais foram carregadas
if not DB_USER or not DB_PASSWORD:
    logger.critical("DB_USER ou DB_PASSWORD não definidos no .env ou variáveis de ambiente. A aplicação pode falhar ao conectar ao banco.")
    # Em uma aplicação real, poderia levantar uma exceção ou sair aqui.
    # messagebox não deve ser usado em módulos de configuração/backend.