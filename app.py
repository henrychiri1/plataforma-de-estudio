import streamlit as st
import os
import re

st.title("🎓 Simulador de Ascenso 2026")

ruta = "templates"
if os.path.exists(ruta):
    archivos = [f for f in os.listdir(ruta) if f.endswith(".txt")]
    archivo = st.sidebar.selectbox("Elige un grupo:", archivos)
    
    if archivo:
        with open(os.path.join(ruta, archivo), "r", encoding="utf-8", errors="ignore") as f:
            texto = f.read()
        
        # Dividimos el texto usando "Pregunta #" como marcador
        preguntas = re.split(r'(?=Pregunta #)', texto)
        
        # Inicializamos el estado para la pregunta actual
        if 'idx' not in st.session_state: st.session_state.idx = 0
        
        # Mostramos la pregunta actual
        st.markdown(preguntas[st.session_state.idx])
        
        # Botones de navegación
        col1, col2 = st.columns(2)
        if col1.button("Anterior") and st.session_state.idx > 0:
            st.session_state.idx -= 1
            st.rerun()
        if col2.button("Siguiente") and st.session_state.idx < len(preguntas) - 1:
            st.session_state.idx += 1
            st.rerun()
