from flask import Flask, render_template, request, jsonify, session
from database import get_db

# --- AGREGA ESTA LÍNEA AQUÍ ---
from werkzeug.security import generate_password_hash, check_password_hash
# ------------------------------



app = Flask(__name__)
app.secret_key = 's3cr3t_k3y'


@app.route('/')
def homepage():
    """Página principal - muestra home.html"""
    return render_template('home.html')  # ← home.html es la página inicial



@app.route('/cadastro')
def cadastro_page():
    """Página de registro"""
    return render_template('cadastro.html')















@app.route('/cadastrar', methods=['POST'])
def cadastrar_usuario():
    """Ruta para procesar el registro del usuario"""
    
    # 1. Obtener datos del formulario
    nome = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')

    # 2. Validaciones básicas
    if not nome or not email or not password:
        return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'})

    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Las contraseñas no coinciden'})

    try:
        db = get_db()
        cursor = db.cursor()

        # 3. Verificar si el email ya existe
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            cursor.close()
            db.close()
            return jsonify({'success': False, 'message': 'Este email ya está registrado'})

        # 4. Encriptar la contraseña (Hash)
        # Esto convierte "12345" en algo como "pbkdf2:sha256:..."
        senha_hash = generate_password_hash(password)

        # 5. Insertar en la base de datos
        # Asumiendo que tu tabla tiene columnas: nome, email, senha
        sql = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nome, email, senha_hash))
        
        db.commit() # ¡Importante! Guarda los cambios
        
        cursor.close()
        db.close()

        return jsonify({'success': True, 'message': '¡Cuenta creada con éxito!'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error en el servidor: {str(e)}'})










@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # Si es GET, solo muestra la página
    if request.method == 'GET':
        return render_template('logIn.html')
    
    # Si es POST, procesa el login (lo que envía el JS)
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Faltan datos'})

    try:
        db = get_db()
        cursor = db.cursor()
        
        # 1. Buscar usuario por email
        cursor.execute("SELECT id, nome, senha FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone() # Devuelve un diccionario: {'id': 1, 'nome': 'Juan', 'senha': '...'}
        
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
                
                return jsonify({'success': True, 'message': '¡Bienvenido!'})
            else:
                return jsonify({'success': False, 'message': 'Contraseña incorrecta'})
        else:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/logout')
def logout():
    session.clear() # Cierra la sesión
    return render_template('home.html') # O redirigir a login















@app.route('/usuarios')
def listar_usuarios():
    """Ruta para ver todos los usuarios (solo para testing)"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, data_cadastro FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(usuarios)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)