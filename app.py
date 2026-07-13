import streamlit as st
import os

st.title("Simulador de Ascenso")

ruta = "templates"
if os.path.exists(ruta):
    archivos = [f for f in os.listdir(ruta) if f.endswith(".txt")]
    archivo = st.sidebar.selectbox("Elige archivo", archivos)
    
    if archivo:
        with open(os.path.join(ruta, archivo), "r", encoding="utf-8", errors="ignore") as f:
            st.text(f.read())
else:
    st.write("No existe la carpeta templates")
