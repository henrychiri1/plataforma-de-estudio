import os
from flask import Flask, request, jsonify, render_template
from supabase import create_client

app = Flask(__name__)

# Configuración de variables de entorno desde Render
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# NUEVA RUTA: Sirve la interfaz web
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Tu lógica de validación se mantiene igual
@app.route('/validar', methods=['POST'])
def validar_codigo():
    data = request.json
    codigo = data.get('codigo')
    
    # 1. Consultar si el código existe
    usuario = supabase.table("Usuarios").select("*").eq("codigo_acceso", codigo).execute()
    
    if not usuario.data:
        return jsonify({"mensaje": "Código no encontrado"}), 404
        
    # 2. Verificar si ya está siendo usado por alguien más
    if usuario.data[0]['estado_sesion'] == True:
        return jsonify({"mensaje": "El código ya está en uso"}), 403
        
    # 3. Si todo está bien, activar sesión
    supabase.table("Usuarios").update({"estado_sesion": True}).eq("codigo_acceso", codigo).execute()
    return jsonify({"mensaje": "Acceso permitido"})

if __name__ == '__main__':
    app.run(debug=True)
=======
import os
import re
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from supabase import create_client

app = Flask(__name__)

# Configuración de CORS: Solo permite peticiones desde tu propia URL
CORS(app, resources={r"/validar": {"origins": "https://plataforma-de-estudio.onrender.com"}})

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/validar', methods=['POST'])
def validar_codigo():
    data = request.json
    # Usamos .get() con valor por defecto para evitar errores si el campo está vacío
    codigo = data.get('codigo', '')

    # SEGURIDAD: Validación de formato antes de tocar la base de datos
    # Ajusta esta expresión regular según cómo sean tus códigos (ej: 8 caracteres alfanuméricos)
    if not re.match("^[a-zA-Z0-9]{8,12}$", codigo):
        return jsonify({"mensaje": "Formato de código inválido"}), 400
    
    # LÓGICA DE SUPABASE
    usuario = supabase.table("Usuarios").select("*").eq("codigo_acceso", codigo).execute()
    
    if not usuario.data:
        return jsonify({"mensaje": "Código no encontrado"}), 404
        
    if usuario.data[0].get('estado_sesion') == True:
        return jsonify({"mensaje": "El código ya está en uso"}), 403
        
    supabase.table("Usuarios").update({"estado_sesion": True}).eq("codigo_acceso", codigo).execute()
    return jsonify({"mensaje": "Acceso permitido"})

if __name__ == '__main__':
    app.run(debug=True)

