import os
from flask import Flask, request, jsonify
from supabase import create_client

app = Flask(__name__)

# Configuración de variables de entorno desde Render
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Inicializar cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ruta raíz para evitar el error 404 "Extraviado"
@app.route('/', methods=['GET'])
def index():
    return jsonify({"mensaje": "Bienvenido a la API de mi plataforma de estudio"})

# Ruta para validar códigos
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
