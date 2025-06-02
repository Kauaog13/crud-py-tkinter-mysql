import tkinter as tk
from tkinter import messagebox
from ttkthemes import ThemedTk
from gui.main_window import AplicacaoAlunos
from database import db_handler, db_config

def main():
    conexao_teste = db_handler.conectar_db()

    if not conexao_teste:
        tk.messagebox.showerror("Erro Crítico de Banco de Dados",
                                f"Não foi possível conectar ao banco de dados '{db_config.DB_NAME}' "
                                f"nas configurações fornecidas em 'database/db_config.py'.\n"
                                f"Host: {db_config.DB_HOST}, Usuário: {db_config.DB_USER}\n\n"
                                "Verifique se o banco de dados '{db_config.DB_NAME}' existe, "
                                "se as credenciais estão corretas e se o servidor MySQL está rodando.\n\n"
                                "A aplicação será encerrada.")
        return 

    if conexao_teste.is_connected():
        conexao_teste.close()   
    print(f"Conexão bem-sucedida ao banco de dados '{db_config.DB_NAME}'. A aplicação será iniciada.")
    
    try:
        root = ThemedTk(theme="arc")
    except tk.TclError:
        print("Tema 'arc' não encontrado ou erro no ttkthemes. Usando tema padrão do Tk.")
        root = tk.Tk()

    app = AplicacaoAlunos(root)
    root.mainloop()

if __name__ == "__main__":
    main()