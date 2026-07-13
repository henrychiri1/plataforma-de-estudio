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
                op_map = {}
                for l in lineas:
                    if l.startswith("A)"): op_map['A'] = l[3:]
                    if l.startswith("B)"): op_map['B'] = l[3:]
                    if l.startswith("C)"): op_map['C'] = l[3:]
                    if l.startswith("D)"): op_map['D'] = l[3:]
                corr_letra = re.search(r'Respuesta correcta:\s*([A-D])', b).group(1)
                texto_correcto = op_map[corr_letra]
                just = re.search(r'Justificación:\s*(.*)', b, re.DOTALL).group(1).strip()
                preguntas.append({'q': pregunta, 'opciones': list(op_map.values()), 'corr_texto': texto_correcto, 'just': just})
            except: continue
    return preguntas

st.title("🎓 Simulador de Ascenso 2026")

# Inicializar contadores
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'correctas' not in st.session_state: st.session_state.correctas = 0
if 'incorrectas' not in st.session_state: st.session_state.incorrectas = 0
if 'respondidas' not in st.session_state: st.session_state.respondidas = set()

ruta = "templates"
if os.path.exists(ruta):
    archivos = [f for f in os.listdir(ruta) if f.endswith(".txt")]
    archivo = st.sidebar.selectbox("Selecciona bloque:", archivos)
    
    if archivo:
        data = parse_txt(open(os.path.join(ruta, archivo), "r", encoding="utf-8", errors="ignore").read())
        
        # Barra de progreso y métricas
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Correctas", st.session_state.correctas)
        col_m2.metric("Errores", st.session_state.incorrectas)
        st.progress((st.session_state.idx) / len(data))

        if st.session_state.idx < len(data):
            q = data[st.session_state.idx]
            opciones_mezcladas = q['opciones'][:]
            random.shuffle(opciones_mezcladas)
            
            st.subheader(f"Pregunta {st.session_state.idx + 1}")
            st.write(q['q'])
            
            seleccion = st.radio("Elige:", opciones_mezcladas, index=None, key=f"q_{st.session_state.idx}")
            
            if st.button("Comprobar") and seleccion:
                if st.session_state.idx not in st.session_state.respondidas:
                    if seleccion == q['corr_texto']:
                        st.session_state.correctas += 1
                        st.success("¡Correcto! 🎉")
                    else:
                        st.session_state.incorrectas += 1
                        st.error(f"Incorrecto. La correcta era: {q['corr_texto']}")
                    st.info(f"**Justificación:** {q['just']}")
                    st.session_state.respondidas.add(st.session_state.idx)
                    st.rerun()
            
            if st.button("Siguiente"):
                st.session_state.idx += 1
                st.rerun()
        else:
            # Pantalla final
            st.balloons()
            st.header("¡Has completado el bloque!")
            porcentaje = (st.session_state.correctas / len(data)) * 100
            st.write(f"Tu puntuación final: {porcentaje:.1f}%")
            if porcentaje >= 80:
                st.success("¡Excelente! Estás listo para el ascenso. 🚀")
            else:
                st.warning("Buen intento, pero necesitas reforzar un poco más. ¡Sigue practicando! 💪")
            if st.button("Reiniciar Simulacro"):
                st.session_state.idx = 0
                st.session_state.correctas = 0
                st.session_state.incorrectas = 0
                st.session_state.respondidas = set()
                st.rerun()
