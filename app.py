import streamlit as st
import os
import re

st.set_page_config(page_title="Simulador Ascenso 2026", layout="centered")

def parse_txt(contenido):
    # Usamos una técnica sin barras invertidas para limpiar el texto
    # Eliminamos el patrón convirtiendo los corchetes
    contenido_limpio = contenido.replace("[", "(").replace("]", ")")
    
    # Bloques divididos por "Pregunta #"
    bloques = re.split("Pregunta #", contenido_limpio)
    preguntas = []
    
    for b in bloques:
        if "Respuesta correcta:" in b:
            # Extraemos datos usando un enfoque más sencillo
            pregunta = b.split("\n")[0]
            partes = b.split("\n")
            
            # Buscamos las opciones basándonos en la letra inicial
            op_a = next((p for p in partes if p.startswith("A)")), "")
            op_b = next((p for p in partes if p.startswith("B)")), "")
            op_c = next((p for p in partes if p.startswith("C)")), "")
            op_d = next((p for p in partes if p.startswith("D)")), "")
            
            corr = next((p for p in partes if "Respuesta correcta:" in p), "A")
            just = next((p for p in partes if "Justificación:" in p), "Sin justificación")
            
            preguntas.append({
                "pregunta": pregunta,
                "a": op_a, "b": op_b, "c": op_c, "d": op_d,
                "corr": corr[-1], 
                "just": just
            })
    return preguntas

st.title("🎓 Simulador de Ascenso 2026")
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
                st.info(f"**{q['just']}**")
                
            if st.button("Siguiente"):
                if st.session_state.q_idx < len(data) - 1:
                    st.session_state.q_idx += 1
                    st.rerun()
