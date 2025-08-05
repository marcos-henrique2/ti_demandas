# create_tables.py
from app import app, db

print("Iniciando a criação das tabelas no banco de dados...")

# Entra no contexto da aplicação para ter acesso ao banco
with app.app_context():
    db.create_all()

print("Tabelas criadas com sucesso!")
