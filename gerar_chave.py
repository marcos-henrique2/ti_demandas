# gerar_chave.py
from cryptography.fernet import Fernet

# Gera uma nova chave
key = Fernet.generate_key()

# Salva a chave em um arquivo chamado secret.key
with open('secret.key', 'wb') as key_file:
    key_file.write(key)

print("Chave de criptografia gerada e salva no arquivo 'secret.key'!")
print("Copie o conteúdo deste arquivo para a sua variável de ambiente SECRET_KEY.")
