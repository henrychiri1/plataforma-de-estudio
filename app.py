import streamlit as st
import os
import re

st.set_page_config(page_title="Simulador Ascenso 2026", layout="centered")

def parse_txt(contenido):
    contenido_limpio = re.sub(r"\", "", contenido)
    bloques = re.split(r"Pregunta #", contenido_limpio)
    preguntas = []
    
    for b in bloques:
        if "Respuesta correcta:" in b:
            lineas = b.splitlines()
            pregunta = lineas[0]
            opciones = {"A": "", "B": "", "C": "", "D": ""}
            for linea in lineas:
                if linea.startswith("A)"): opciones["A"] = linea[2:]
                if linea.startswith("B)"): opciones["B"] = linea[2:]
                if linea.startswith("C)"): opciones["C"] = linea[2:]
                if linea.startswith("D)"): opciones["D"] = linea[2:]
            
            corr = "A"
            for linea in lineas:
                if "Respuesta correcta:" in linea:
                    match = re.search(r"([a-dA-D])", linea)
                    if match: corr = match.group(1).upper()
            
            just = "Verificar en documento original"
            for linea in lineas:
                if "Justificación:" in linea:
                    just = linea.split(":", 1)[1].strip()
            
            preguntas.append({
                "pregunta": pregunta,
                "a": opciones["A"], "b": opciones["B"], "c": opciones["C"], "d": opciones["D"],
                "corr": corr, "just": just
            })
    return preguntas

st.title("🎓 Simulador de Ascenso 2026")

ruta_templates = "templates"
if os.path.exists(ruta_templates):
    archivos = [f for f in os.listdir(ruta_templates) if f.endswith(".txt")]
    bloque = st.sidebar.selectbox("Elige un bloque:", archivos)

    if bloque:
        # AQUÍ ESTÁ EL CAMBIO CLAVE: 'errors="ignore"' hará que no se bloquee por caracteres raros
        with open(os.path.join(ruta_templates, bloque), "r", encoding="utf-8", errors="ignore") as f:
            data = parse_txt(f.read())
        
        if "q_idx" not in st.session_state: st.session_state.q_idx = 0
        
        if data:
            q = data[st.session_state.q_idx]
            st.subheader(f"Pregunta {st.session_state.q_idx + 1}: {q['pregunta']}")
            opciones = {"A": q['a'], "B": q['b'], "C": q['c'], "D": q['d']}
            eleccion = st.radio("Selecciona:", list(opciones.keys()), format_func=lambda x: f"{x}) {opciones[x]}")
            
            if st.button("Verificar"):
                if eleccion == q['corr']:
                    st.success("¡Correcto! 🎉")
                else:
                    st.error(f"Incorrecto. La correcta era {q['corr']}")
                st.info(f"**Justificación:** {q['just']}")
                
            if st.button("Siguiente"):
                if st.session_state.q_idx < len(data) - 1:
                    st.session_state.q_idx += 1
                    st.rerun()
