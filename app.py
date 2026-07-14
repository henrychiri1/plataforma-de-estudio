import streamlit as st
import os
import re
import random

st.set_page_config(page_title="Simulador Ascenso", layout="centered")

def parse_txt(contenido):
    # Regex ajustado a tu formato: "Pregunta #X:"
    bloques = re.split(r'Pregunta #\d+:', contenido)
    preguntas = []
    for b in bloques:
        if "Respuesta correcta:" in b:
            try:
                lineas = [l.strip() for l in b.strip().split('\n') if l.strip()]
                pregunta = lineas[0]
                op_map = {}
                for l in lineas:
                    # Detecta A), B), C), D) al inicio
                    match = re.match(r'^([A-D])\)\s*(.*)', l)
                    if match:
                        op_map[match.group(1)] = match.group(2)
                
                corr_match = re.search(r'Respuesta correcta:\s*([A-D])', b)
                corr_letra = corr_match.group(1)
                texto_correcto = op_map.get(corr_letra)
                
                just_match = re.search(r'Justificación:\s*(.*)', b, re.DOTALL)
                just = just_match.group(1).strip() if just_match else "Sin justificación"
                
                if len(op_map) == 4:
                    preguntas.append({'q': pregunta, 'opciones': list(op_map.values()), 'corr_texto': texto_correcto, 'just': just})
            except: continue
    return preguntas

# --- ESTADO INICIAL ---
if 'idx' not in st.session_state: 
    st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0, 'respondido': False, 'last_file': None, 'intentos': 0})

st.title("🎓 Simulador de Ascenso 2026")

ruta = "templates"
if os.path.exists(ruta):
    archivos = sorted([f for f in os.listdir(ruta) if f.endswith(".txt")])
    archivo = st.sidebar.selectbox("Bloque:", archivos)
    
    if st.session_state.last_file != archivo:
        st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0, 'respondido': False, 'last_file': archivo, 'intentos': 0})
        st.rerun()

    data = parse_txt(open(os.path.join(ruta, archivo), "r", encoding="utf-8", errors="ignore").read())
    
    if len(data) > 0:
        st.progress(min(st.session_state.idx / len(data), 1.0))
        c1, c2 = st.columns(2)
        c1.metric("Correctas ✅", st.session_state.correctas)
        c2.metric("Errores ❌", st.session_state.incorrectas)

        if st.session_state.idx < len(data):
            q = data[st.session_state.idx]
            if st.session_state.get('last_q_idx') != st.session_state.idx:
                st.session_state.mezcladas = q['opciones'][:]
                random.shuffle(st.session_state.mezcladas)
                st.session_state.last_q_idx = st.session_state.idx
                st.session_state.respondido = False
                st.session_state.intentos = 0

            st.subheader(f"Pregunta {st.session_state.idx + 1}")
            st.write(q['q'])
            
            seleccion = st.radio("Elige:", st.session_state.mezcladas, index=None, key=f"radio_{st.session_state.idx}_{st.session_state.intentos}", disabled=st.session_state.respondido)
            
            if seleccion:
                if seleccion == q['corr_texto']:
                    st.success("¡Correcto! 🎉")
                    st.session_state.correctas += 1
                    st.session_state.respondido = True
                else:
                    if st.session_state.intentos == 0:
                        st.warning("Incorrecto. ¡Piénsalo mejor y vuelve a elegir!")
                        st.session_state.intentos += 1
                        st.rerun()
                    else:
                        st.error(f"Incorrecto. La respuesta era: {q['corr_texto']}")
                        st.session_state.incorrectas += 1
                        st.session_state.respondido = True
                
                if st.session_state.respondido:
                    st.info(f"**Justificación:** {q['just']}")
                    if st.button("Siguiente Pregunta"):
                        st.session_state.idx += 1
                        st.rerun()
        else:
            st.balloons()
            st.success("¡Bloque completado!")
            if st.button("Reiniciar"):
                st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0})
                st.rerun()
    else:
        st.warning("No se pudieron cargar preguntas. Revisa el formato del archivo.")
