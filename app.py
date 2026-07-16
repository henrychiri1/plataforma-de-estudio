import streamlit as st
import os
import re
import random

st.set_page_config(page_title="Simulador Ascenso", layout="centered")

# --- AUTENTICACIÓN (LOGIN) ---
CLAVE_MAESTRA = "ASCENSO2026" 

def ventana_login():
    st.title("🔐 Acceso al Simulador")
    st.info("Por favor, introduce la clave para acceder al material.")
    clave = st.text_input("Clave de acceso:", type="password")
    if st.button("Ingresar"):
        if clave == CLAVE_MAESTRA:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Clave incorrecta.")
    st.stop()

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado: ventana_login()

# --- LÓGICA DE DATOS ---
@st.cache_data
def parse_txt(ruta_archivo):
    contenido = open(ruta_archivo, "r", encoding="utf-8-sig", errors="ignore").read()
    bloques = re.split(r'Pregunta\s*#\d+:', contenido, flags=re.IGNORECASE)
    preguntas = []
    for b in bloques:
        if "Respuesta correcta:" in b:
            try:
                pregunta = b.split('A)')[0].strip()
                opciones = {}
                for letra in ['A', 'B', 'C', 'D']:
                    pattern = f"{letra}\)(.*?)(?=[B-D]\)|Respuesta correcta:|$)"
                    match = re.search(pattern, b, re.IGNORECASE | re.DOTALL)
                    if match: opciones[letra] = match.group(1).strip()
                
                corr_match = re.search(r'Respuesta\s*correcta:\s*([A-Da-d])', b, re.IGNORECASE)
                corr_letra = corr_match.group(1).upper()
                texto_correcto = opciones.get(corr_letra, "No encontrada")
                just = re.search(r'Justificación:\s*(.*)', b, re.IGNORECASE | re.DOTALL)
                just_text = just.group(1).strip() if just else "Sin justificación"
                
                preguntas.append({'q': pregunta, 'opciones': list(opciones.values()), 'corr_texto': texto_correcto, 'just': just_text})
            except: continue
    return preguntas

# --- CONTADOR DE VISITAS ---
def actualizar_visitas():
    if not os.path.exists("visitas.txt"):
        with open("visitas.txt", "w") as f: f.write("1")
        return 1
    with open("visitas.txt", "r+") as f:
        v = int(f.read()) + 1
        f.seek(0); f.write(str(v))
        return v

if 'num_visitas' not in st.session_state:
    st.session_state.num_visitas = actualizar_visitas()

# --- INTERFAZ PRINCIPAL ---
st.title("🎓 Simulador de Ascenso 2026")
st.sidebar.metric("Usuarios Totales", st.session_state.num_visitas)

if 'idx' not in st.session_state: 
    st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0, 'respondido': False, 'last_file': None, 'mezcladas': []})

# SELECCIÓN DE CARPETAS
ruta_base = "templates"
tipo_contenido = st.sidebar.radio("Selecciona tipo:", ["grupos", "simulacros"])
carpeta_actual = os.path.join(ruta_base, tipo_contenido)

if os.path.exists(carpeta_actual):
    archivos = sorted([f for f in os.listdir(carpeta_actual) if f.endswith(".txt")])
    archivo = st.sidebar.selectbox(f"Selecciona {tipo_contenido}:", archivos)
    ruta_archivo = os.path.join(carpeta_actual, archivo)

    if st.session_state.last_file != ruta_archivo:
        st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0, 'respondido': False, 'last_file': ruta_archivo, 'last_q_idx': None})
        st.rerun()

    data = parse_txt(ruta_archivo)
    
    if data:
        st.progress(min(st.session_state.idx / len(data), 1.0))
        c1, c2 = st.columns(2)
        c1.metric("Correctas ✅", st.session_state.correctas)
        c2.metric("Errores ❌", st.session_state.incorrectas)

        if st.session_state.idx < len(data):
            q = data[st.session_state.idx]
            if st.session_state.get('last_q_idx') != st.session_state.idx:
                st.session_state.respondido = False
                st.session_state.last_q_idx = st.session_state.idx
                st.session_state.mezcladas = q['opciones'][:]
                if tipo_contenido == "grupos": random.shuffle(st.session_state.mezcladas)

            st.subheader(f"Pregunta {st.session_state.idx + 1}")
            st.write(q['q'])
            
            opciones_para_mostrar = st.session_state.get('mezcladas', q['opciones'])
            seleccion = st.radio("Elige:", opciones_para_mostrar, index=None, key=f"r_{st.session_state.idx}", disabled=st.session_state.respondido)
            
            if seleccion:
                if not st.session_state.respondido:
                    if seleccion == q['corr_texto']:
                        st.success("¡Excelente trabajo! ¡Vas por muy buen camino! 🎉")
                        st.session_state.correctas += 1
                    else:
                        # Feedback con color rojo intenso usando HTML
                        st.markdown(f"<h3 style='color:red;'>¡Incorrecto!</h3>", unsafe_allow_html=True)
                        st.error(f"La respuesta correcta era: {q['corr_texto']}")
                        st.session_state.incorrectas += 1
                    st.session_state.respondido = True
                    st.rerun()
                
                if st.session_state.respondido:
                    st.info(f"**Justificación:** {q['just']}")
                    if st.button("Siguiente Pregunta"):
                        st.session_state.idx += 1
                        st.rerun()
        else:
            st.balloons()
            st.success("¡Has completado el bloque con éxito!")
            if st.button("Reiniciar"):
                st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0})
                st.rerun()
