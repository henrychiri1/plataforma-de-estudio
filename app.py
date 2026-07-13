import streamlit as st
import os
import re

st.set_page_config(page_title="Simulador Ascenso 2026", layout="centered")

def parse_txt(contenido):
    # Esta función limpia las etiquetas y extrae las preguntas
    contenido_limpio = re.sub(r'\', '', contenido)
    bloques = re.split(r'(?=Pregunta\s*#)', contenido_limpio)
    preguntas = []
    for b in bloques:
        match = re.search(r'Pregunta\s*#\d+:\s*(?P<pregunta>.*?)\nA\)\s*(?P<a>.*?)\nB\)\s*(?P<b>.*?)\nC\)\s*(?P<c>.*?)\nD\)\s*(?P<d>.*?)\nRespuesta correcta:\s*(?P<corr>[a-dA-D]).*?\nJustificación:\s*(?P<just>.*)', b, re.DOTALL)
        if match:
            preguntas.append(match.groupdict())
    return preguntas

st.title("🎓 Simulador de Ascenso 2026")
st.sidebar.header("Selección de Bloque")

# Buscar archivos en la carpeta templates
archivos = [f for f in os.listdir('templates') if f.endswith('.txt')]
bloque = st.sidebar.selectbox("Elige un bloque de preguntas:", archivos)

if bloque:
    with open(os.path.join('templates', bloque), 'r', encoding='utf-8') as f:
        data = parse_txt(f.read())
    
    if 'q_idx' not in st.session_state: st.session_state.q_idx = 0
    
    q = data[st.session_state.q_idx]
    
    st.progress((st.session_state.q_idx + 1) / len(data))
    st.subheader(f"Pregunta {st.session_state.q_idx + 1}: {q['pregunta']}")
    
    opciones = {"A": q['a'], "B": q['b'], "C": q['c'], "D": q['d']}
    eleccion = st.radio("Selecciona una opción:", list(opciones.keys()), format_func=lambda x: f"{x}) {opciones[x]}")
    
    if st.button("Verificar"):
        if eleccion == q['corr'].upper():
            st.success("¡Correcto! 🎉")
        else:
            st.error(f"Incorrecto. La correcta era {q['corr'].upper()}")
        st.info(f"**Justificación:** {q['just']}")
        
    if st.button("Siguiente pregunta"):
        if st.session_state.q_idx < len(data) - 1:
            st.session_state.q_idx += 1
            st.rerun()
