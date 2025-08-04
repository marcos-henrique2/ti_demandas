# criar_usuarios.py
from app import app, db, Usuario
from getpass import getpass # Módulo para esconder a senha digitada no terminal

def adicionar_usuario():
    """Função para adicionar um novo usuário ao banco de dados."""
    with app.app_context():
        print("--- Adicionar Novo Usuário ---")
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
        novo_usuario.set_password(password) # Usa o método para gerar o hash
        
        db.session.add(novo_usuario)
        db.session.commit()
        print(f"Usuário '{username}' criado com sucesso!")

if __name__ == '__main__':
    adicionar_usuario()