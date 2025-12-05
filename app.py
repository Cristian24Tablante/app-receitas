from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db  # Importa a função do arquivo database.py acima

app = Flask(__name__)
app.secret_key = 's3cr3t_k3y' # Recomendação: Em produção, use variáveis de ambiente

# ---------------- ROTAS DE PÁGINAS (GET) ----------------

@app.route('/')
def homepage():
    """Página principal"""
    return render_template('home.html')

@app.route('/cadastro')
def cadastro_page():
    """Página de registro (formulário)"""
    return render_template('cadastro.html')

@app.route('/login', methods=['GET'])
def login_page_view():
    """Mostra o formulário de login"""
    return render_template('logIn.html')

# ---------------- ROTAS DE API / LÓGICA (POST) ----------------

@app.route('/cadastrar', methods=['POST'])
def cadastrar_usuario():
    """Processa o registro do usuário"""
    
    # 1. Obter dados
    nome = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')

    # 2. Validações básicas
    if not nome or not email or not password:
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'})

    if password != confirm_password:
        return jsonify({'success': False, 'message': 'As senhas não coincidem'})

    try:
        db = get_db()
        cursor = db.cursor()

        # 3. Verificar se email já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({'success': False, 'message': 'Este email já está registrado'})

        # 4. Encriptar senha
        senha_hash = generate_password_hash(password)

        # 5. Inserir no banco
        sql = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nome, email, senha_hash))
        
        db.commit() # Salva as alterações
        
        cursor.close()
        db.close()

        return jsonify({'success': True, 'message': 'Conta criada com sucesso!'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro no servidor: {str(e)}'})

@app.route('/login', methods=['POST'])
def login_process():
    """Processa o login do usuário"""
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Faltam dados'})

    try:
        db = get_db()
        cursor = db.cursor()
        
        # 1. Buscar usuário
        cursor.execute("SELECT id, nome, senha FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        
        cursor.close()
        db.close()

        if usuario and check_password_hash(usuario['senha'], password):
            # 2. Login bem sucedido
            session['user_id'] = usuario['id']
            session['user_name'] = usuario['nome']
            return jsonify({'success': True, 'message': 'Bem-vindo!'})
        else:
            return jsonify({'success': False, 'message': 'Email ou senha incorretos'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@app.route('/logout')
def logout():
    session.clear()
    return render_template('home.html')

# ---------------- OUTRAS ROTAS ----------------

@app.route('/usuarios')
def listar_usuarios():
    """Rota de teste para listar usuários"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, data_cadastro FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(usuarios)
    except Exception as e:
        return f"Erro: {str(e)}"

# Rotas de Receitas (Simples renderização)
@app.route('/EatPrayLove')
def eatpraylove_page(): return render_template('EatPrayLove.html')

@app.route('/ratatouille')
def ratatouille_page(): return render_template('ratatouille.html')

@app.route('/kung')
def kungfu_page(): return render_template('kung.html')

@app.route('/matilda')
def matilda_page(): return render_template('matilda.html')

@app.route('/beignets')
def beignets_page(): return render_template('beignets.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)