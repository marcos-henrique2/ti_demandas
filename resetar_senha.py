# resetar_senha.py
from app import app, db, Usuario
from getpass import getpass # Para esconder a digitação da senha

def resetar_senha_usuario():
    """Script de linha de comando para resetar a senha de um usuário existente."""
    # Garante que estamos no contexto da aplicação para acessar o banco de dados
    with app.app_context():
        print("--- Reset de Senha de Usuário ---")
        username = input("Digite o nome do usuário que terá a senha resetada: ")

        # Procura o usuário no banco de dados
        user = Usuario.query.filter_by(username=username).first()

        # Verifica se o usuário foi encontrado
        if not user:
            print(f"Erro: Usuário '{username}' não encontrado no sistema.")
            return

        print(f"Usuário '{user.username}' encontrado. Por favor, defina a nova senha.")
        
        # Pede a nova senha de forma segura
        password = getpass("Digite a NOVA senha: ")
        password_confirm = getpass("Confirme a NOVA senha: ")

        if password != password_confirm:
            print("Erro: As senhas não coincidem. Operação cancelada.")
            return

        # Usa o método que já criamos no nosso modelo para setar a nova senha hasheada
        user.set_password(password)
        
        # Salva a alteração no banco de dados
        db.session.commit()
        
        print(f"\nSucesso! A senha do usuário '{username}' foi alterada.")

if __name__ == '__main__':
    resetar_senha_usuario()