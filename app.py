import os
from flask import Flask, request, jsonify, render_template
from supabase import create_client

app = Flask(__name__)

# Configuración de variables de entorno desde Render
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Inicializar cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ruta para servir la página web (Interfaz)
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Ruta para validar códigos (Backend)
@app.route('/validar', methods=['POST'])
def validar_codigo():
    data = request.json
    codigo = data.get('codigo')
    
    usuario = supabase.table("Usuarios").select("*").eq("codigo_acceso", codigo).execute()
    
    if not usuario.data:
        return jsonify({"mensaje": "Código no encontrado"}), 404
        
    if usuario.data[0]['estado_sesion'] == True:
        return jsonify({"mensaje": "El código ya está en uso"}), 403
        
    supabase.table("Usuarios").update({"estado_sesion": True}).eq("codigo_acceso", codigo).execute()
    return jsonify({"mensaje": "Acceso permitido"})

if __name__ == '__main__':
    app.run(debug=True)
