# app_alunos.py
import tkinter as tk
from tkinter import messagebox
from ttkthemes import ThemedTk
from gui.main_window import AplicacaoAlunos
from database import db_handler, db_config # Importa db_handler e db_config
import logging
import logging.handlers
import os

LOG_FILENAME = 'app_alunos.log'

def configurar_logging():
    """Configura o sistema de logging para a aplicação."""
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_FILENAME)
    logger_raiz = logging.getLogger()
    logger_raiz.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(module)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    # Evita adicionar handlers duplicados se a função for chamada múltiplas vezes (pouco provável aqui)
    if not logger_raiz.handlers:
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO) 
        console_handler.setFormatter(formatter)
        logger_raiz.addHandler(console_handler)

        # Handler para arquivo
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path, maxBytes=5*1024*1024, backupCount=2)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger_raiz.addHandler(file_handler)
    
    logging.info("="*50)
    logging.info("Sistema de Logging configurado. Aplicação iniciando.")
    logging.info("="*50)

def main():
    configurar_logging() # Configura o logging primeiro
    logger = logging.getLogger(__name__)
    logger.info("Função main() iniciada.")

    conexao_teste = db_handler.conectar_db()
    if not conexao_teste:
        logger.critical(f"Falha CRÍTICA na conexão inicial com o BD: Host={db_config.DB_HOST}, User={db_config.DB_USER}, DB={db_config.DB_NAME}. A aplicação será encerrada.")
        tk.messagebox.showerror("Erro Crítico de Banco de Dados",
                                f"Não foi possível conectar ao banco de dados '{db_config.DB_NAME}'.\n"
                                "Verifique as configurações, se o BD existe e se o servidor MySQL está rodando.\n\n"
                                f"Consulte o arquivo '{LOG_FILENAME}' para mais detalhes técnicos.\n\n"
                                "A aplicação será encerrada.")
        return 

    if conexao_teste.is_connected():
        conexao_teste.close()
    logger.info("Teste de conexão inicial com o banco de dados bem-sucedido.")
    logger.info(f"Aplicação assume que o banco '{db_config.DB_NAME}' e a tabela 'alunos' já existem.")
    
    try:
        root = ThemedTk(theme="arc")
        logger.info("Janela principal (ThemedTk) criada com tema 'arc'.")
    except tk.TclError as e:
        logger.warning(f"Tema 'arc' não encontrado ou erro no ttkthemes: {e}. Usando tema padrão do Tk.")
        root = tk.Tk()
    except Exception as e:
        logger.exception("Ocorreu um erro inesperado ao criar a janela principal (ThemedTk).")
        tk.messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao iniciar a interface gráfica (ThemedTk).\nVerifique '{LOG_FILENAME}'.")
        return

    try:
        app = AplicacaoAlunos(root)
        logger.info("Instância de AplicacaoAlunos criada.")
        root.mainloop()
        logger.info("Janela principal fechada. Encerrando aplicação.")
    except Exception as e:
        logger.exception("Ocorreu um erro fatal durante a execução da aplicação.")
        # Tenta mostrar um messagebox, mas a GUI pode estar instável
        try:
            tk.messagebox.showerror("Erro Fatal", f"Um erro fatal ocorreu.\nConsulte '{LOG_FILENAME}' para detalhes.")
        except: # noqa
            pass # Se nem o messagebox funcionar, o log já foi registrado.
        # print(f"ERRO FATAL: {e}. Verifique '{LOG_FILENAME}'.") # O logger já captura isso

if __name__ == "__main__":
    main()