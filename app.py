import streamlit as st
import os
import re
import random

st.set_page_config(page_title="Simulador Ascenso", layout="centered")

# --- AUTENTICACIÓN ---
CLAVE_MAESTRA = "ASCENSO2026" 
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if not st.session_state.autenticado:
    st.title("🔐 Acceso al Simulador")
    clave = st.text_input("Clave de acceso:", type="password")
    if st.button("Ingresar"):
        if clave == CLAVE_MAESTRA:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Clave incorrecta.")
    st.stop()

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
                just_text = just.group(1).strip() if just else "Sin justificación detallada."
                
                preguntas.append({'q': pregunta, 'opciones': list(opciones.values()), 'corr_texto': texto_correcto, 'just': just_text})
            except: continue
    return preguntas

# --- INTERFAZ ---
st.title("🎓 Simulador de Ascenso 2026")
ruta_base = "templates"
tipo = st.sidebar.radio("Selecciona tipo:", ["grupos", "simulacros"])
carpeta = os.path.join(ruta_base, tipo)

if os.path.exists(carpeta):
    archivos = sorted([f for f in os.listdir(carpeta) if f.endswith(".txt")])
    archivo = st.sidebar.selectbox(f"Selecciona {tipo}:", archivos)
    ruta_archivo = os.path.join(carpeta, archivo)
    
    if 'last_file' not in st.session_state or st.session_state.last_file != ruta_archivo:
        st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0, 'respondido': False, 'last_file': ruta_archivo, 'last_q_idx': None, 'mezcladas': []})
        st.rerun()

    data = parse_txt(ruta_archivo)
    
    if data and st.session_state.idx < len(data):
        q = data[st.session_state.idx]
        if st.session_state.get('last_q_idx') != st.session_state.idx:
            st.session_state.respondido = False
            st.session_state.last_q_idx = st.session_state.idx
            st.session_state.mezcladas = q['opciones'][:]
            if tipo == "grupos": random.shuffle(st.session_state.mezcladas)

        st.subheader(f"Pregunta {st.session_state.idx + 1}")
        st.write(q['q'])
        
        # Corrección del AttributeError usando .get()
        opciones_para_mostrar = st.session_state.get('mezcladas', q['opciones'])
        seleccion = st.radio("Elige:", opciones_para_mostrar, index=None, key=f"r_{st.session_state.idx}", disabled=st.session_state.respondido)
        
        if seleccion:
            if not st.session_state.respondido:
                if seleccion == q['corr_texto']:
                    st.success("¡Excelente trabajo! ¡Vas por muy buen camino! 🎉")
                    st.session_state.correctas += 1
                else:
                    st.error(f"¡Ánimo, no te rindas! La respuesta correcta era: {q['corr_texto']}")
                    st.session_state.incorrectas += 1
                st.session_state.respondido = True
                st.rerun()
            
            if st.session_state.respondido:
                st.info(f"**Justificación Académica:**\n\n{q['just']}")
                if st.button("Siguiente Pregunta"):
                    st.session_state.idx += 1
                    st.rerun()
    elif data:
        st.balloons()
        st.success("¡Has completado el bloque con éxito!")
        if st.button("Reiniciar"):
            st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0})
            st.rerun()
