from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

# --- FUNÇÃO DE CONEXÃO COM O BANCO DE DADOS (Duplicada para auto-contenção, mas idealmente deve estar em database.py) ---
def get_db():
    return mysql.connector.connect(
        host='tini.click',
        user='spoiler_com_sabor',
        password='4287816f7bc22c82a83f70ad492266db',
        database='spoiler_com_sabor'
    )
# ---------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)
# Certifique-se de que a chave secreta é forte em produção
app.secret_key = 's3cr3t_k3y'


# --- Funções Auxiliares para Autenticação ---
def login_required(f):
    """Decorator para exigir que o usuário esteja logado"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Se não estiver logado, redireciona para a página de login
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function
# -------------------------------------------


@app.route('/')
def homepage():
    """Página principal - mostra home.html"""
    return render_template('home.html') 


@app.route('/cadastro')
def cadastro_page():
    """Página de registro"""
    return render_template('cadastro.html')


@app.route('/cadastrar', methods=['POST'])
def cadastrar_usuario():
    """Ruta para procesar el registro del usuario"""
    
    nome = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')

    if not nome or not email or not password:
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'})

    if password != confirm_password:
        return jsonify({'success': False, 'message': 'As senhas não coincidem'})

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # 3. Verificar se o email já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            cursor.close()
            db.close()
            return jsonify({'success': False, 'message': 'Este email já está registrado'})

        # 4. Encriptar a senha (Hash)
        senha_hash = generate_password_hash(password)

        # 5. Insertar en la base de datos
        sql = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nome, email, senha_hash))
        
        db.commit() 
        
        cursor.close()
        db.close()

        return jsonify({'success': True, 'message': '¡Cuenta creada con éxito!'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'})


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # Se já estiver logado, redireciona para a home
    if 'user_id' in session:
        return redirect(url_for('homepage'))
        
    # Se for GET, só mostra a página
    if request.method == 'GET':
        return render_template('logIn.html')
    
    # Se for POST, processa o login (o que envia o JS)
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Faltan dados'})

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # 1. Buscar usuario por email
        cursor.execute("SELECT id, nome, senha FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone() 
        
        cursor.close()
        db.close()

        if usuario:
            # 2. Verificar la contraseña (Hash vs Texto plano)
            senha_hash = usuario['senha']
            
            if check_password_hash(senha_hash, password):
                # ¡Contraseña correcta!
                # 3. Guardar usuario en la SESIÓN (Login exitoso)
                session['user_id'] = usuario['id']
                session['user_name'] = usuario['nome']
                
                return jsonify({'success': True, 'message': '¡Bienvenido!', 'redirect': url_for('homepage')})
            else:
                return jsonify({'success': False, 'message': 'Contraseña incorrecta'})
        else:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/logout')
def logout():
    session.clear() # Cierra la sesión
    return redirect(url_for('login_page')) # Redireciona para login após logout


@app.route('/trocar_senha', methods=['GET'])
@login_required # Garante que só usuários logados acessem esta página
def change_password_page():
    """Página para o usuário trocar sua senha"""
    return render_template('trocarSenha.html')


@app.route('/trocar_senha', methods=['POST'])
@login_required # Garante que só usuários logados acessem esta funcionalidade
def trocar_senha():
    """Lógica para processar a troca de senha."""
    
    user_id = session['user_id']
    current_password = request.form.get('currentPassword')
    new_password = request.form.get('newPassword')
    # Nota: A confirmação de senha é validada no lado do cliente (JS), mas uma validação robusta é feita no backend

    # 1. Validação de dados básicos
    if not current_password or not new_password:
        return jsonify({'success': False, 'message': 'Por favor, preencha todos os campos de senha.'})

    if len(new_password) < 6: # Exemplo de política de senha
        return jsonify({'success': False, 'message': 'A nova senha deve ter no mínimo 6 caracteres.'})

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # 2. Buscar a senha HASH atual do usuário
        cursor.execute("SELECT senha FROM usuarios WHERE id = %s", (user_id,))
        usuario = cursor.fetchone()

        if not usuario:
            # Isso não deve acontecer se @login_required funcionar, mas é uma proteção
            return jsonify({'success': False, 'message': 'Erro de autenticação. Usuário não encontrado.'})

        # 3. Verificar se a senha atual fornecida está correta
        senha_hash_atual = usuario['senha']
        
        if not check_password_hash(senha_hash_atual, current_password):
            cursor.close()
            db.close()
            return jsonify({'success': False, 'message': 'A senha atual está incorreta.'})

        # 4. Gerar o hash da nova senha
        nova_senha_hash = generate_password_hash(new_password)

        # 5. Atualizar a senha no banco de dados
        sql = "UPDATE usuarios SET senha = %s WHERE id = %s"
        cursor.execute(sql, (nova_senha_hash, user_id))
        
        db.commit() 
        
        cursor.close()
        db.close()

        return jsonify({'success': True, 'message': 'Senha alterada com sucesso! Você deve fazer login novamente.'})

    except Exception as e:
        print(f"Erro ao trocar senha: {e}")
        return jsonify({'success': False, 'message': f'Erro no servidor ao atualizar a senha: {str(e)}'})



@app.route('/usuarios')
@login_required # Rota só para logados, idealmente deve ser restrito a admins
def listar_usuarios():
    """Ruta para ver todos los usuarios (solo para testing)"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email, data_cadastro FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(usuarios)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/EatPrayLove')
def eatpraylove_page():
    """Página de receitas de Eat Pray Love"""
    return render_template('EatPrayLove.html')

 
@app.route('/ratatouille')
def ratatouille_page():
    """Página especial de Ratatouille"""
    return render_template('ratatouille.html')


@app.route('/kung')
def kungfu_page():
    """Página de receitas de Kung Fu Panda"""
    return render_template('kung.html')

@app.route('/matilda')
def matilda_page():
    """Página de receitas de Matilda"""
    return render_template('matilda.html')


@app.route('/beignets')
def beignets_page():
    """Página de receitas de Beignets"""
    return render_template('beignets.html')

@app.route('/breakbad')
def breakbad_page():
    """Página de receitas de Breaking Bad"""
    return render_template('breakbad.html')

@app.route('/thewalkingdead')
def thewalkingdead_page():
    """Página de receitas de The Walking Dead"""
    return render_template('thewallkingdead.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)