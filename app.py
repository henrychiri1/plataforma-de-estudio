import streamlit as st
import os
import re
import random

st.set_page_config(page_title="Simulador Ascenso", layout="centered")

def parse_txt(contenido):
    bloques = re.split(r'Pregunta #', contenido)
    preguntas = []
    for b in bloques:
        if "Respuesta correcta:" in b:
            try:
                lineas = b.split('\n')
                pregunta = lineas[0]
                op_map = {}
                for l in lineas:
                    if l.startswith("A)"): op_map['A'] = l[3:]
                    if l.startswith("B)"): op_map['B'] = l[3:]
                    if l.startswith("C)"): op_map['C'] = l[3:]
                    if l.startswith("D)"): op_map['D'] = l[3:]
                corr_letra = re.search(r'Respuesta correcta:\s*([A-D])', b).group(1)
                texto_correcto = op_map[corr_letra]
                just = re.search(r'Justificación:\s*(.*)', b, re.DOTALL).group(1).strip()
                preguntas.append({'q': pregunta, 'opciones': list(op_map.values()), 'corr_texto': texto_correcto, 'just': just})
            except: continue
    return preguntas

# Funciones de callback para que sea automático
def verificar():
    seleccion = st.session_state.seleccion
    q = st.session_state.pregunta_actual
    if seleccion == q['corr_texto']:
        st.session_state.correctas += 1
    else:
        st.session_state.incorrectas += 1
    st.session_state.respondido = True

st.title("🎓 Simulador de Ascenso 2026")

if 'idx' not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.correctas = 0
    st.session_state.incorrectas = 0
    st.session_state.respondido = False

ruta = "templates"
if os.path.exists(ruta):
    archivos = [f for f in os.listdir(ruta) if f.endswith(".txt")]
    archivo = st.sidebar.selectbox("Selecciona bloque:", archivos)
    
    if archivo:
        data = parse_txt(open(os.path.join(ruta, archivo), "r", encoding="utf-8", errors="ignore").read())
        q = data[st.session_state.idx]
        st.session_state.pregunta_actual = q
        
        # Mezclar opciones solo al cargar la pregunta
        if 'mezcladas' not in st.session_state or st.session_state.idx != st.session_state.get('last_idx'):
            st.session_state.mezcladas = q['opciones'][:]
            random.shuffle(st.session_state.mezcladas)
            st.session_state.last_idx = st.session_state.idx
            st.session_state.respondido = False

        st.subheader(f"Pregunta {st.session_state.idx + 1}")
        st.write(q['q'])
        
        # Radio automático
        st.radio("Elige:", st.session_state.mezcladas, index=None, on_change=verificar, key="seleccion", disabled=st.session_state.respondido)
        
        # Mostrar resultado solo si ya respondió
        if st.session_state.respondido:
            if st.session_state.seleccion == q['corr_texto']:
                st.success("¡Correcto! 🎉")
            else:
                st.error(f"Incorrecto. Correcta: {q['corr_texto']}")
            st.info(f"**Justificación:** {q['just']}")
            
            if st.button("Siguiente"):
                st.session_state.idx += 1
                st.session_state.respondido = False
                st.rerun()

        st.sidebar.metric("Correctas", st.session_state.correctas)
        st.sidebar.metric("Errores", st.session_state.incorrectas)
