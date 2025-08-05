import os
from app import app, db, Usuario

# Pega as credenciais do admin das variáveis de ambiente
# Usa 'admin' como padrão caso as variáveis não sejam encontradas
admin_user = os.environ.get('ADMIN_USER', 'admin')
admin_pass = os.environ.get('ADMIN_PASS', 'admin')

with app.app_context():
    print("Criando todas as tabelas do banco de dados...")
    db.create_all()
    print("Tabelas criadas.")

    print(f"Verificando se o usuário '{admin_user}' existe...")
    if not Usuario.query.filter_by(username=admin_user).first():
        print("Usuário não encontrado, criando novo usuário admin...")
        novo_admin = Usuario(username=admin_user)
        novo_admin.set_password(admin_pass)
        db.session.add(novo_admin)
        db.session.commit()
        print(f"Usuário '{admin_user}' criado com sucesso.")
    else:
        print("Usuário admin já existe.")

print("Script de inicialização concluído.")