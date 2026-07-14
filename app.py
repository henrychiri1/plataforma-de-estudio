import streamlit as st
import os
import re
import random

st.set_page_config(page_title="Simulador Ascenso", layout="centered")

def parse_txt(contenido):
    bloques = re.split(r'Pregunta #', contenido)
    preguntas = []
    for b in bloques:
        if "Respuesta correcta:" in b.lower():
            try:
                lineas = b.strip().split('\n')
                pregunta = lineas[0]
                op_map = {}
                # Lógica flexible: detecta A), A., a), a.
                for l in lineas:
                    match = re.match(r'^([A-Da-d])[\.\)]\s*(.*)', l.strip())
                    if match:
                        letra = match.group(1).upper()
                        op_map[letra] = match.group(2).strip()
                
                # Si no encontramos al menos 4 opciones, omitimos la pregunta para evitar errores
                if len(op_map) < 4: continue

                corr_match = re.search(r'Respuesta correcta:\s*([A-Da-d])', b, re.IGNORECASE)
                corr_letra = corr_match.group(1).upper()
                texto_correcto = op_map.get(corr_letra, "No encontrada")
                
                just = re.search(r'Justificación:\s*(.*)', b, re.DOTALL)
                just_text = just.group(1).strip() if just else "Sin justificación"
                
                preguntas.append({'q': pregunta, 'opciones': list(op_map.values()), 'corr_texto': texto_correcto, 'just': just_text})
            except: continue
    return preguntas

# --- ESTADO INICIAL ---
if 'idx' not in st.session_state: 
    st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0, 'respondido': False, 'last_file': None})

st.title("🎓 Simulador de Ascenso 2026")

ruta = "templates"
if os.path.exists(ruta):
    archivos = sorted([f for f in os.listdir(ruta) if f.endswith(".txt")])
    archivo = st.sidebar.selectbox("Bloque:", archivos)
    
    # Reset al cambiar de archivo
    if st.session_state.last_file != archivo:
        st.session_state.update({'idx': 0, 'correctas': 0, 'incorrectas': 0, 'respondido': False, 'last_file': archivo, 'mezcladas': None})
        st.rerun()

    data = parse_txt(open(os.path.join(ruta, archivo), "r", encoding="utf-8", errors="ignore").read())
    
    # Barra de progreso
    if len(data) > 0:
    st.progress(min(st.session_state.idx / len(data), 1.0))
    else:
    st.warning("El archivo seleccionado está vacío o no tiene preguntas válidas. Por favor, revisa el formato del archivo .txt")
    
    # Contadores
    c1, c2 = st.columns(2)
    c1.metric("Correctas ✅", st.session_state.correctas)
    c2.metric("Errores ❌", st.session_state.incorrectas)

    if st.session_state.idx < len(data):
        q = data[st.session_state.idx]
        
        # Mezclar solo si es pregunta nueva
        if st.session_state.get('last_q_idx') != st.session_state.idx:
            st.session_state.mezcladas = q['opciones'][:]
            random.shuffle(st.session_state.mezcladas)
            st.session_state.last_q_idx = st.session_state.idx
            st.session_state.respondido = False
            st.session_state.intentos = 0

        st.subheader(f"Pregunta {st.session_state.idx + 1}")
        st.write(q['q'])
        
        # KEY DINÁMICA: Obliga a Streamlit a refrescar el radio
        seleccion = st.radio("Elige:", st.session_state.mezcladas, index=None, key=f"radio_{st.session_state.idx}")
        
        if seleccion:
            if not st.session_state.respondido:
                if seleccion == q['corr_texto']:
                    st.success("¡Correcto! 🎉")
                    st.session_state.correctas += 1
                    st.session_state.respondido = True
                else:
                    if st.session_state.intentos == 0:
                        st.warning("Incorrecto. Tienes una segunda oportunidad.")
                        st.session_state.intentos += 1
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
