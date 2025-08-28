import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Ganancias App", layout="wide")
st.title("💰 Simulador de Ganancias con Retiradas y Referidos")

# ==========================
# Saldo inicial
# ==========================
saldo_inicial = st.number_input(
    "Saldo inicial del usuario",
    min_value=0.0,
    value=0.0,
    step=None,          # permite escribir cualquier valor libremente
    format="%.2f"
)

# ==========================
# Retiradas configurables
# ==========================
st.subheader("Configuración de retiradas automáticas")

if "retiros_config" not in st.session_state:
    st.session_state.retiros_config = []

# Añadir nueva retirada
col1, col2 = st.columns([2, 1])
with col1:
    monto_disparo = st.number_input(
        "Monto de saldo para disparar la retirada",
        min_value=0.0,
        value=0.0,
        step=1.0,
        format="%.2f"
    )
with col2:
    importe_retiro = st.number_input(
        "Importe a retirar",
        min_value=0.0,
        value=0.0,
        step=1.0,
        format="%.2f"
    )

if st.button("➕ Añadir retirada"):
    if monto_disparo > 0 and importe_retiro > 0:
        st.session_state.retiros_config.append({
            "Monto disparo": monto_disparo,
            "Importe retiro": importe_retiro
        })

# Mostrar retiradas configuradas
st.subheader("Retiros configurados")
if len(st.session_state.retiros_config) > 0:
    df_retiros = pd.DataFrame(st.session_state.retiros_config)
    st.dataframe(df_retiros, use_container_width=True)
else:
    st.info("No hay retiradas configuradas todavía.")

# ==========================
# Gestión de referidos
# ==========================
st.subheader("Referidos")

comisiones = {"A": 19, "B": 7, "C": 3}

if "referidos" not in st.session_state:
    st.session_state.referidos = []

if st.button("➕ Añadir referido"):
    st.session_state.referidos.append({"nombre": "", "nivel": "A"})

nuevos_referidos = []
for i, ref in enumerate(st.session_state.referidos):
    cols = st.columns([2, 1, 1])
    with cols[0]:
        nombre = st.text_input(f"Nombre referido {i+1}", value=ref["nombre"], key=f"nombre_{i}")
    with cols[1]:
        nivel = st.selectbox(f"Nivel {i+1}", ["A", "B", "C"], index=["A","B","C"].index(ref["nivel"]), key=f"nivel_{i}")
    with cols[2]:
        st.write(f"Comisión: {comisiones[nivel]}%")
    nuevos_referidos.append({"nombre": nombre, "nivel": nivel})

st.session_state.referidos = nuevos_referidos

# Mostrar tabla de referidos
st.subheader("Resumen de Referidos")
if len(st.session_state.referidos) > 0:
    df_refs = pd.DataFrame([
        {"Nombre": r["nombre"], "Nivel": r["nivel"], "Comisión %": comisiones[r["nivel"]]}
        for r in st.session_state.referidos
    ])
    st.dataframe(df_refs, use_container_width=True)
else:
    st.info("No hay referidos añadidos todavía.")
