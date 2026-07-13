import streamlit as st
import os
import re
import random

st.set_page_config(page_title="Simulador Ascenso", layout="centered")

# ... [La función parse_txt se mantiene igual] ...
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

# --- ESTADO ---
if 'idx' not in st.session_state: 
    st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0, 'intentos': 0, 'respondido': False, 'last_file': None})

st.title("🎓 Simulador de Ascenso 2026")

ruta = "templates"
if os.path.exists(ruta):
   # Con sorted() le indicamos que ordene la lista alfabéticamente
    archivos = sorted([f for f in os.listdir(ruta) if f.endswith(".txt")])
    archivo = st.sidebar.selectbox("Bloque:", archivos)
    
    if archivo:
        data = parse_txt(open(os.path.join(ruta, archivo), "r", encoding="utf-8", errors="ignore").read())
        
        if st.session_state.last_file != archivo:
            st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0, 'last_file': archivo, 'respondido': False, 'intentos': 0})
            st.rerun()

        # BARRA DE PROGRESO
        progreso = (st.session_state.idx) / len(data)
        st.progress(progreso)
        
        col1, col2 = st.columns(2)
        col1.metric("Correctas ✅", st.session_state.correctas)
        col2.metric("Errores ❌", st.session_state.incorrectas)

        if st.session_state.idx < len(data):
            q = data[st.session_state.idx]
            
            if 'mezcladas' not in st.session_state or st.session_state.get('last_idx') != st.session_state.idx:
                st.session_state.mezcladas = q['opciones'][:]
                random.shuffle(st.session_state.mezcladas)
                st.session_state.last_idx = st.session_state.idx
                st.session_state.intentos = 0
                st.session_state.respondido = False

            st.subheader(f"Pregunta {st.session_state.idx + 1}")
            st.write(q['q'])
            
            # Lógica de respuesta
            seleccion = st.radio("Elige:", st.session_state.mezcladas, index=None, key="seleccion", disabled=st.session_state.respondido)
            
            if seleccion:
                if seleccion == q['corr_texto']:
                    st.success("¡Excelente! Has acertado. 🎉")
                    st.session_state.correctas += 1 if st.session_state.intentos == 0 else 0
                    st.session_state.respondido = True
                else:
                    if st.session_state.intentos == 0:
                        st.warning("Esa no es la opción correcta. ¡Piénsalo un poco más y vuelve a intentarlo! Tienes una oportunidad más.")
                        st.session_state.intentos += 1
                        st.rerun() # Recargamos para que pueda volver a elegir
                    else:
                        st.error(f"Incorrecto. La respuesta era: {q['corr_texto']}")
                        st.session_state.incorrectas += 1
                        st.session_state.respondido = True
            
            if st.session_state.respondido:
                st.info(f"**Justificación:** {q['just']}")
                if st.button("Siguiente"):
                    st.session_state.idx += 1
                    st.session_state.respondido = False
                    st.rerun()
        else:
            st.balloons()
            st.write("### ¡Bloque completado!")
