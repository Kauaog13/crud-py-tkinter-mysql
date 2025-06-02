# app_alunos.py
import tkinter as tk
from tkinter import messagebox
from ttkthemes import ThemedTk
from gui.main_window import AplicacaoAlunos
from database import db_handler, db_config 
import logging
import logging.handlers
import os # Para garantir que o log seja criado no diretório do script

# Define o nome do arquivo de log que será criado na pasta raiz do projeto
LOG_FILENAME = 'app_alunos.log'

def configurar_logging():
    """Configura o sistema de logging para a aplicação."""
    
    # Garante que o arquivo de log seja criado no mesmo diretório do app_alunos.py
    # os.path.abspath(__file__) dá o caminho absoluto deste arquivo de script
    # os.path.dirname(...) pega o diretório desse caminho
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_FILENAME)

    logger_raiz = logging.getLogger() # Obtém o logger raiz
    logger_raiz.setLevel(logging.DEBUG) # Define o nível mínimo de log a ser capturado

    # Formato das mensagens de log
    # Ex: 2025-06-02 17:15:00 - gui.main_window - main_window.metodo:123 - INFO - Mensagem.
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(module)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Evita adicionar handlers duplicados se esta função for chamada mais de uma vez
    # (o que não deve acontecer neste setup, mas é uma boa prática)
    if not logger_raiz.handlers:
        # Handler para console (exibe logs no terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO) # Nível para o console (ex: INFO, WARNING, ERROR, CRITICAL)
        console_handler.setFormatter(formatter)
        logger_raiz.addHandler(console_handler)

        # Handler para arquivo (salva logs em um arquivo com rotação)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path, 
            maxBytes=5*1024*1024,  # Tamanho máximo do arquivo de log (ex: 5MB)
            backupCount=2  # Número de arquivos de backup a serem mantidos (ex: app_alunos.log, app_alunos.log.1)
        )
        file_handler.setLevel(logging.DEBUG) # Nível para o arquivo (captura tudo a partir de DEBUG)
        file_handler.setFormatter(formatter)
        logger_raiz.addHandler(file_handler)
    
    # Log inicial para confirmar que o logging foi configurado
    # Esta mensagem só aparecerá se os handlers foram adicionados (ou seja, na primeira vez)
    if logger_raiz.handlers: # Confirma que os handlers foram adicionados
        logging.info("="*60)
        logging.info("Sistema de Logging configurado. Aplicação iniciando...")
        logging.info(f"Logs serão salvos em: {log_file_path}")
        logging.info("="*60)

def main():
    """Função principal que inicia a aplicação."""
    # 1. Configura o logging como a primeira ação
    configurar_logging()
    logger = logging.getLogger(__name__) # Logger específico para esta função/módulo
    logger.info("Função main() iniciada.")

    # 2. Testa a conexão inicial com o banco de dados
    logger.debug("Testando conexão inicial com o banco de dados...")
    conexao_teste = db_handler.conectar_db() # db_handler já usa logging
    
    if not conexao_teste:
        # O db_handler.conectar_db() já loga o erro detalhado.
        # Aqui, informamos o usuário e encerramos de forma mais crítica.
        logger.critical(f"Falha CRÍTICA na conexão inicial com o BD (detalhes no log anterior). Aplicação será encerrada.")
        tk.messagebox.showerror("Erro Crítico de Banco de Dados",
                                f"Não foi possível conectar ao banco de dados '{db_config.DB_NAME}'.\n"
                                "Verifique as configurações no arquivo .env, se o banco de dados existe "
                                "e se o servidor MySQL está em execução.\n\n"
                                f"Consulte o arquivo '{LOG_FILENAME}' para detalhes técnicos.\n\n"
                                "A aplicação será encerrada.")
        return 
    
    # Se a conexão foi bem-sucedida, fecha a conexão de teste.
    if conexao_teste.is_connected():
        conexao_teste.close()
        logger.debug("Conexão de teste com o BD fechada.")
    logger.info("Teste de conexão inicial com o banco de dados bem-sucedido.")
    logger.info(f"Aplicação assume que o banco '{db_config.DB_NAME}' e a tabela 'alunos' já existem (não tenta criá-los).")

    # 3. Configura e inicia a janela principal da aplicação gráfica
    root = None
    try:
        logger.debug("Criando janela principal com ThemedTk (tema 'arc').")
        root = ThemedTk(theme="arc") # Define o tema inicial da aplicação
    except tk.TclError as e:
        logger.warning(f"Tema 'arc' não encontrado ou erro no ttkthemes: {e}. Usando tema padrão do Tkinter.")
        root = tk.Tk() # Fallback para o Tkinter padrão se o tema falhar
    except Exception as e:
        logger.exception("Ocorreu um erro inesperado ao criar a janela principal com ThemedTk.")
        tk.messagebox.showerror("Erro Crítico de Interface", 
                                f"Ocorreu um erro ao iniciar a interface gráfica (ThemedTk).\n"
                                f"Consulte '{LOG_FILENAME}' para detalhes.\n\n"
                                "A aplicação será encerrada.")
        return

    try:
        logger.debug("Instanciando AplicacaoAlunos.")
        app = AplicacaoAlunos(root) # Cria a instância da classe principal da GUI
        logger.info("Interface gráfica AplicacaoAlunos criada e pronta para ser exibida.")
        root.mainloop() # Inicia o loop de eventos do Tkinter
        logger.info("Janela principal fechada pelo usuário. Encerrando aplicação.")
    except Exception as e:
        logger.exception("Ocorreu um erro fatal durante a execução do loop principal da GUI.")
        # Tenta mostrar um messagebox como último recurso, mas a GUI pode estar instável.
        try:
            tk.messagebox.showerror("Erro Fatal na Aplicação", 
                                    f"Um erro fatal e inesperado ocorreu.\n"
                                    f"Consulte o arquivo '{LOG_FILENAME}' para detalhes técnicos.\n\n"
                                    "A aplicação pode precisar ser encerrada.")
        except: # noqa
            pass # Se nem o messagebox funcionar, o erro já foi logado.

if __name__ == "__main__":
    # Este bloco é executado quando o script app_alunos.py é rodado diretamente
    main()