import streamlit as st
import os
import re

st.set_page_config(page_title="Simulador Ascenso 2026", layout="centered")

def parse_txt(contenido):
    # Usamos comillas dobles y el prefijo r para evitar errores de escape
    contenido_limpio = re.sub(r"\", "", contenido)
    bloques = re.split(r"(?=Pregunta\s*#)", contenido_limpio)
    preguntas = []
    for b in bloques:
        # Regex seguro para capturar el formato que tienes en tus archivos
        match = re.search(r"Pregunta\s*#\d+:\s*(?P<pregunta>.*?)\nA\)\s*(?P<a>.*?)\nB\)\s*(?P<b>.*?)\nC\)\s*(?P<c>.*?)\nD\)\s*(?P<d>.*?)\nRespuesta correcta:\s*(?P<corr>[a-dA-D]).*?\nJustificación:\s*(?P<just>.*)", b, re.DOTALL)
        if match:
            preguntas.append(match.groupdict())
    return preguntas

st.title("🎓 Simulador de Ascenso 2026")
st.sidebar.header("Selección de Bloque")

ruta_templates = "templates"
if os.path.exists(ruta_templates):
    archivos = [f for f in os.listdir(ruta_templates) if f.endswith(".txt")]
    bloque = st.sidebar.selectbox("Elige un bloque:", archivos)

    if bloque:
        with open(os.path.join(ruta_templates, bloque), "r", encoding="utf-8") as f:
            data = parse_txt(f.read())
        
        if "q_idx" not in st.session_state: st.session_state.q_idx = 0
        
        q = data[st.session_state.q_idx]
        st.subheader(f"Pregunta {st.session_state.q_idx + 1}: {q['pregunta']}")
        
        opciones = {"A": q['a'], "B": q['b'], "C": q['c'], "D": q['d']}
        eleccion = st.radio("Selecciona:", list(opciones.keys()), format_func=lambda x: f"{x}) {opciones[x]}")
        
        if st.button("Verificar"):
            if eleccion == q['corr'].upper():
                st.success("¡Correcto! 🎉")
            else:
                st.error(f"Incorrecto. La correcta era {q['corr'].upper()}")
            st.info(f"**Justificación:** {q['just']}")
            
        if st.button("Siguiente"):
            if st.session_state.q_idx < len(data) - 1:
                st.session_state.q_idx += 1
                st.rerun()
else:
    st.error("No se encontró la carpeta 'templates'.")
