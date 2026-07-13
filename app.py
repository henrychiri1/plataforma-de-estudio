import streamlit as st
import os
import re
import random

st.set_page_config(page_title="Simulador Ascenso", layout="centered")

def parse_txt(contenido):
    bloques = re.split(r'Pregunta #', contenido)
    preguntas = []
    for b in bloques:
        if "A)" in b and "Respuesta correcta:" in b:
            try:
                # Extraemos partes con Regex simple
                pregunta = b.split('\n')[0]
                op_a = re.search(r'A\)\s*(.*?)(?=\nB\))', b, re.DOTALL).group(1)
                op_b = re.search(r'B\)\s*(.*?)(?=\nC\))', b, re.DOTALL).group(1)
                op_c = re.search(r'C\)\s*(.*?)(?=\nD\))', b, re.DOTALL).group(1)
                op_d = re.search(r'D\)\s*(.*?)(?=\nRespuesta)', b, re.DOTALL).group(1)
                corr = re.search(r'Respuesta correcta:\s*([A-D])', b).group(1)
                just = re.search(r'Justificación:\s*(.*)', b, re.DOTALL).group(1).strip()
                
                preguntas.append({'q': pregunta, 'opts': {'A': op_a, 'B': op_b, 'C': op_c, 'D': op_d}, 'corr': corr, 'just': just})
            except: continue
    return preguntas

st.title("🎓 Simulador de Ascenso 2026")

if 'idx' not in st.session_state: st.session_state.idx = 0

ruta = "templates"
if os.path.exists(ruta):
    archivos = [f for f in os.listdir(ruta) if f.endswith(".txt")]
    archivo = st.sidebar.selectbox("Selecciona bloque:", archivos)
    
    if archivo:
        with open(os.path.join(ruta, archivo), "r", encoding="utf-8", errors="ignore") as f:
            data = parse_txt(f.read())
        
        q = data[st.session_state.idx]
        
        # Aleatorizar opciones
        opts = list(q['opts'].items())
        random.shuffle(opts)
        
        st.subheader(f"Pregunta {st.session_state.idx + 1}")
        st.write(q['q'])
        
        # Radio para opciones
        seleccion = st.radio("Elige una opción:", [o[0] for o in opts], format_func=lambda x: f"{x}) {q['opts'][x]}", key=f"q_{st.session_state.idx}")
        
        if st.button("Comprobar Respuesta"):
            if seleccion == q['corr']:
                st.success("¡Correcto! 🎉")
            else:
                st.error(f"Incorrecto. La respuesta era {q['corr']}: {q['opts'][q['corr']]}")
            st.info(f"**Justificación:** {q['just']}")
        
        col1, col2 = st.columns(2)
        if col1.button("Anterior") and st.session_state.idx > 0:
            st.session_state.idx -= 1
            st.rerun()
        if col2.button("Siguiente") and st.session_state.idx < len(data) - 1:
            st.session_state.idx += 1
            st.rerun()
