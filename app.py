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
                # Extraer opciones eliminando los prefijos "A) ", "B) ", etc.
                op_map = {}
                for l in lineas:
                    if l.startswith("A)"): op_map['A'] = l[3:]
                    if l.startswith("B)"): op_map['B'] = l[3:]
                    if l.startswith("C)"): op_map['C'] = l[3:]
                    if l.startswith("D)"): op_map['D'] = l[3:]
                
                corr_letra = re.search(r'Respuesta correcta:\s*([A-D])', b).group(1)
                texto_correcto = op_map[corr_letra]
                
                just = re.search(r'Justificación:\s*(.*)', b, re.DOTALL).group(1).strip()
                
                # Guardamos la pregunta, las opciones como lista y el texto de la correcta
                preguntas.append({
                    'q': pregunta, 
                    'opciones': list(op_map.values()), 
                    'corr_texto': texto_correcto, 
                    'just': just
                })
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
        
        # Aleatorizamos la lista de opciones para que el orden cambie siempre
        opciones_mezcladas = q['opciones'][:]
        random.shuffle(opciones_mezcladas)
        
        st.subheader(f"Pregunta {st.session_state.idx + 1}")
        st.write(q['q'])
        
        # El usuario elige de una lista sin letras A, B, C, D
        seleccion = st.radio("Selecciona una opción:", opciones_mezcladas, index=None)
        
        if st.button("Comprobar Respuesta"):
            if seleccion == q['corr_texto']:
                st.success("¡Correcto! 🎉")
            else:
                st.error(f"Incorrecto. La respuesta correcta era: {q['corr_texto']}")
            st.info(f"**Justificación:** {q['just']}")
        
        # Navegación
        col1, col2 = st.columns(2)
        if col1.button("Anterior") and st.session_state.idx > 0:
            st.session_state.idx -= 1
            st.rerun()
        if col2.button("Siguiente") and st.session_state.idx < len(data) - 1:
            st.session_state.idx += 1
            st.rerun()
