import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
import enum
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# --- Carregando a Chave de Criptografia ---
secret_key_str = os.environ.get('SECRET_KEY')
if not secret_key_str:
    raise RuntimeError("Variável de ambiente SECRET_KEY não definida.")
key = secret_key_str.encode('utf-8')
fernet = Fernet(key)

# --- Configuração ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default-flask-secret-key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- LÓGICA DO BANCO DE DADOS PARA DEPLOY ---
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    raise RuntimeError("Variável de ambiente DATABASE_URL não definida.")
# Ajuste para o SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy(app)
login_manager = LoginManager(); login_manager.init_app(app); login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça o login para acessar esta página."
login_manager.login_message_category = "warning"

# --- Modelos e Rotas ---
# ... COLE AQUI TODOS OS SEUS MODELOS E TODAS AS SUAS ROTAS ...
# (O código dos modelos e das rotas não muda, é o mesmo da nossa última versão funcional)
# ...
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    demandas_criadas = db.relationship('Demanda', backref='criador', lazy=True)
    equipamentos_criados = db.relationship('Equipamento', backref='criador', lazy=True)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id): return Usuario.query.get(int(user_id))
class StatusEquipamento(enum.Enum): EM_USO = "Em uso"; EM_MANUTENCAO = "Em manutenção"; DISPONIVEL = "Disponível"
class StatusDemanda(enum.Enum): A_FAZER = "A fazer"; EM_ANDAMENTO = "Em andamento"; CONCLUIDO = "Concluído"
class PrioridadeDemanda(enum.Enum): BAIXA = "Baixa"; MEDIA = "Média"; ALTA = "Alta"
class Equipamento(db.Model):
    id = db.Column(db.Integer, primary_key=True); modelo = db.Column(db.String(100), nullable=False); loja = db.Column(db.String(100), nullable=False); status = db.Column(db.Enum(StatusEquipamento), default=StatusEquipamento.DISPONIVEL, nullable=False); data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow); user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
class Demanda(db.Model):
    id = db.Column(db.Integer, primary_key=True); descricao = db.Column(db.String(250), nullable=False); status = db.Column(db.Enum(StatusDemanda), default=StatusDemanda.A_FAZER, nullable=False); prioridade = db.Column(db.Enum(PrioridadeDemanda), default=PrioridadeDemanda.MEDIA, nullable=False); data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow); user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
class Credencial(db.Model):
    id = db.Column(db.Integer, primary_key=True); servico = db.Column(db.String(100), nullable=False); login = db.Column(db.String(100)); senha_criptografada = db.Column(db.String(255), nullable=False)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']): login_user(user); return redirect(url_for('index'))
        else: flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')
@app.route('/logout')
@login_required
def logout(): logout_user(); return redirect(url_for('login'))
@app.route('/')
@login_required
def index(): return redirect(url_for('gerenciar_demandas'))
@app.route('/equipamentos', methods=['GET', 'POST'])
@login_required
def gerenciar_equipamentos():
    if request.method == 'POST':
        novo_equipamento = Equipamento(modelo=request.form['modelo'], loja=request.form['loja'], criador=current_user)
        db.session.add(novo_equipamento); db.session.commit(); flash('Equipamento adicionado com sucesso!', 'success')
        return redirect(url_for('gerenciar_equipamentos'))
    equipamentos = Equipamento.query.order_by(Equipamento.data_criacao.desc()).all(); return render_template('equipamentos.html', equipamentos=equipamentos)
@app.route('/demandas', methods=['GET', 'POST'])
@login_required
def gerenciar_demandas():
    if request.method == 'POST':
        nova_demanda = Demanda(descricao=request.form['descricao'], prioridade=PrioridadeDemanda[request.form['prioridade']], criador=current_user)
        db.session.add(nova_demanda); db.session.commit(); flash('Demanda adicionada com sucesso!', 'success')
        return redirect(url_for('gerenciar_demandas'))
    demandas = Demanda.query.order_by(Demanda.data_criacao.desc()).all(); return render_template('demandas.html', demandas=demandas, prioridades=PrioridadeDemanda)
@app.route('/demandas/atualizar/<int:id>', methods=['POST'])
@login_required
def atualizar_status_demanda(id):
    demanda = Demanda.query.get_or_404(id); demanda.status = StatusDemanda[request.form['status']]; db.session.commit()
    return redirect(url_for('gerenciar_demandas'))
@app.route('/demanda/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_demanda(id):
    demanda = Demanda.query.get_or_404(id)
    if request.method == 'POST':
        demanda.descricao = request.form['descricao']; demanda.prioridade = PrioridadeDemanda[request.form['prioridade']]
        db.session.commit(); flash('Demanda atualizada com sucesso!', 'success')
        return redirect(url_for('gerenciar_demandas'))
    return render_template('editar_demanda.html', demanda=demanda, prioridades=PrioridadeDemanda)
@app.route('/demanda/apagar/<int:id>', methods=['POST'])
@login_required
def apagar_demanda(id):
    demanda = Demanda.query.get_or_404(id); db.session.delete(demanda); db.session.commit()
    flash('Demanda apagada com sucesso!', 'success'); return redirect(url_for('gerenciar_demandas'))
@app.route('/equipamento/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_equipamento(id):
    equipamento = Equipamento.query.get_or_404(id)
    if request.method == 'POST':
        equipamento.modelo = request.form['modelo']; equipamento.loja = request.form['loja']
        db.session.commit(); flash('Equipamento atualizado com sucesso!', 'success')
        return redirect(url_for('gerenciar_equipamentos'))
    return render_template('editar_equipamento.html', equipamento=equipamento)
@app.route('/equipamento/apagar/<int:id>', methods=['POST'])
@login_required
def apagar_equipamento(id):
    equipamento = Equipamento.query.get_or_404(id); db.session.delete(equipamento); db.session.commit()
    flash('Equipamento apagado com sucesso!', 'success'); return redirect(url_for('gerenciar_equipamentos'))
@app.route('/credenciais', methods=['GET', 'POST'])
@login_required
def gerenciar_credenciais():
    if request.method == 'POST':
        senha_criptografada = fernet.encrypt(request.form['senha'].encode('utf-8'))
        nova_credencial = Credencial(servico=request.form['servico'], login=request.form['login'], senha_criptografada=senha_criptografada.decode('utf-8'))
        db.session.add(nova_credencial); db.session.commit(); flash('Credencial adicionada com sucesso!', 'success'); return redirect(url_for('gerenciar_credenciais'))
    credenciais = Credencial.query.all(); return render_template('credenciais.html', credenciais=credenciais)
@app.route('/credencial/visualizar/<int:id>', methods=['POST'])
@login_required
def visualizar_credencial(id):
    credencial = Credencial.query.get_or_404(id)
    try:
        senha_pura = fernet.decrypt(credencial.senha_criptografada.encode('utf-8')).decode('utf-8')
        flash(f"A senha para '{credencial.servico}' é: {senha_pura}", 'info')
    except Exception as e: flash(f"Não foi possível descriptografar a senha. Erro: {e}", 'danger')
    return redirect(url_for('gerenciar_credenciais'))
@app.route('/credencial/apagar/<int:id>', methods=['POST'])
@login_required
def apagar_credencial(id):
    credencial = Credencial.query.get_or_404(id); db.session.delete(credencial); db.session.commit()
    flash('Credencial apagada com sucesso!', 'success'); return redirect(url_for('gerenciar_credenciais'))