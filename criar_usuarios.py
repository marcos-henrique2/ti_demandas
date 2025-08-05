# criar_usuarios.py (versão adaptada para deploy)
import os
from app import app, db, Usuario
from getpass import getpass

def adicionar_usuario():
    """Adiciona um novo usuário lendo de variáveis de ambiente ou de forma interativa."""
    with app.app_context():
        # Verifica se as variáveis de ambiente para criação automática existem
        admin_user = os.environ.get('ADMIN_USER')
        admin_pass = os.environ.get('ADMIN_PASS')

        if admin_user and admin_pass:
            # MODO AUTOMÁTICO (para o Render)
            print(f"Criando usuário administrador '{admin_user}' a partir de variáveis de ambiente...")
            if Usuario.query.filter_by(username=admin_user).first():
                print(f"Usuário '{admin_user}' já existe.")
                return
            
            novo_usuario = Usuario(username=admin_user)
            novo_usuario.set_password(admin_pass)
            db.session.add(novo_usuario)
            db.session.commit()
            print("Usuário administrador criado com sucesso!")
        else:
            # MODO INTERATIVO (para uso local)
            print("--- Adicionar Novo Usuário (Modo Interativo) ---")
            username = input("Digite o nome de usuário: ")
            
            if Usuario.query.filter_by(username=username).first():
                print(f"Erro: O usuário '{username}' já existe.")
                return

            password = getpass("Digite a senha: ")
            password_confirm = getpass("Confirme a senha: ")

            if password != password_confirm:
                print("Erro: As senhas não coincidem.")
                return

            novo_usuario = Usuario(username=username)
            novo_usuario.set_password(password)
            db.session.add(novo_usuario)
            db.session.commit()
            print(f"Usuário '{username}' criado com sucesso!")

if __name__ == '__main__':
    adicionar_usuario()