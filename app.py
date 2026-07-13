import streamlit as st
import os
import re

# Configuración visual
st.set_page_config(page_title="Plataforma de Estudio", page_icon="🎓", layout="centered")

def parse_txt(contenido):
    # Regex robusto que captura pregunta, opciones A-D, respuesta y justificación
    # Ignoramos etiquetas como que vienen en tus archivos
    contenido_limpio = re.sub(r'\', '', contenido)
    bloques = re.split(r'(?=Pregunta\s*#)', contenido_limpio)
    
    preguntas = []
    for b in bloques:
        match = re.search(r'Pregunta\s*#\d+:\s*(?P<pregunta>.*?)\nA\)\s*(?P<a>.*?)\nB\)\s*(?P<b>.*?)\nC\)\s*(?P<c>.*?)\nD\)\s*(?P<d>.*?)\nRespuesta correcta:\s*(?P<corr>[a-dA-D])\s*.*?\nJustificación:\s*(?P<just>.*)', b, re.DOTALL)
        if match:
            preguntas.append(match.groupdict())
    return preguntas

# --- INTERFAZ ---
st.title("🎓 Simulador de Ascenso 2026")
st.sidebar.header("Menú de Bloques")

# 1. Cargar archivos desde carpeta 'templates'
ruta_templates = 'templates'
if not os.path.exists(ruta_templates):
    os.makedirs(ruta_templates)

archivos = [f for f in os.listdir(ruta_templates) if f.endswith('.txt')]
bloque_seleccionado = st.sidebar.selectbox("Selecciona tu bloque:", archivos)

if bloque_seleccionado:
    with open(os.path.join(ruta_templates, bloque_seleccionado), 'r', encoding='utf-8') as f:
        data = parse_txt(f.read())
    
    if not data:
        st.error("No se pudieron extraer preguntas. Revisa el formato del archivo TXT.")
    else:
        # Estado de la sesión
        if 'score' not in st.session_state: st.session_state.score = {'corr': 0, 'err': 0}
        if 'q_idx' not in st.session_state: st.session_state.q_idx = 0

        q = data[st.session_state.q_idx]

        # Progreso
        st.progress((st.session_state.q_idx + 1) / len(data))
        st.write(f"Pregunta {st.session_state.q_idx + 1} de {len(data)}")
        
        st.subheader(q['pregunta'])
        
        opc = st.radio("Selecciona:", ["A", "B", "C", "D"], key="q_sel")
        
        if st.button("Comprobar"):
            if opc.lower() == q['corr'].lower():
                st.session_state.score['corr'] += 1
                st.success("¡Correcto! 🎉")
            else:
                st.session_state.score['err'] += 1
                st.error(f"Incorrecto. La correcta era {q['corr'].upper()}")
            
            with st.expander("Ver Justificación", expanded=True):
                st.info(q['just'])
        
        # Métricas
        col1, col2 = st.columns(2)
        col1.metric("Correctas", st.session_state.score['corr'])
        col2.metric("Errores", st.session_state.score['err'])
        
        if st.button("Siguiente"):
            if st.session_state.q_idx < len(data) - 1:
                st.session_state.q_idx += 1
                st.rerun()
            else:
                st.balloons()
                st.write("¡Bloque finalizado!")
