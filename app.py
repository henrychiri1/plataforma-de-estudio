import streamlit as st
import os
import re

st.set_page_config(page_title="Simulador Ascenso 2026", layout="centered")

def parse_txt(contenido):
    # En lugar de re.sub complejo, limpiamos el texto directamente reemplazando las etiquetas source
    # Esto evita el uso de barras invertidas que causan el error de sintaxis
    contenido_limpio = contenido.replace("", "").replace("", "")
    # También podemos borrar cualquier etiqueta con este regex simple
    contenido_limpio = re.sub(r"\", "", contenido_limpio)
    
    bloques = re.split(r"(?=Pregunta\s*#)", contenido_limpio)
    preguntas = []
    for b in bloques:
        # Usamos una estructura más simple para el match
        match = re.search(r"Pregunta\s*#\d+:\s*(.*?)\nA\)\s*(.*?)\nB\)\s*(.*?)\nC\)\s*(.*?)\nD\)\s*(.*?)\nRespuesta correcta:\s*([a-dA-D]).*?\nJustificación:\s*(.*)", b, re.DOTALL)
        if match:
            preguntas.append({
                "pregunta": match.group(1),
                "a": match.group(2),
                "b": match.group(3),
                "c": match.group(4),
                "d": match.group(5),
                "corr": match.group(6),
                "just": match.group(7)
            })
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
        
        if data:
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
            st.warning("No se encontraron preguntas válidas en el archivo seleccionado.")
else:
    st.error("No se encontró la carpeta 'templates'.")
