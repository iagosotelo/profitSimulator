import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Ganancias App", layout="wide")
st.title("💰 Simulador de Ganancias con Referidos y Retiradas")

# ==========================
# Saldo inicial editable libremente
# ==========================
if "saldo_inicial" not in st.session_state:
    st.session_state["saldo_inicial"] = 0.0

st.session_state["saldo_inicial"] = st.number_input(
    "Saldo inicial del usuario (€)",
    min_value=0.0,
    value=st.session_state["saldo_inicial"],
    step=None,
    format="%.2f"
)

# ==========================
# Retiradas configurables
# ==========================
st.subheader("Retiros automáticos configurables")

if "retiros_config" not in st.session_state:
    st.session_state["retiros_config"] = []

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

st.subheader("Retiros configurados")
if len(st.session_state.retiros_config) > 0:
    df_retiros = pd.DataFrame(st.session_state.retiros_config)
    st.dataframe(df_retiros, use_container_width=True)
else:
    st.info("No hay retiradas configuradas todavía.")

# ==========================
# Referidos dinámicos
# ==========================
st.subheader("Referidos")

comisiones = {"A": 19, "B": 7, "C": 3}

if "referidos" not in st.session_state:
    st.session_state["referidos"] = []

if st.button("➕ Añadir referido"):
    st.session_state["referidos"].append({"nombre": "", "nivel": "A"})

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

st.subheader("Resumen de Referidos")
if len(st.session_state.referidos) > 0:
    df_refs = pd.DataFrame([
        {"Nombre": r["nombre"], "Nivel": r["nivel"], "Comisión %": comisiones[r["nivel"]]}
        for r in st.session_state.referidos
    ])
    st.dataframe(df_refs, use_container_width=True)
else:
    st.info("No hay referidos añadidos todavía.")

# ==========================
# Simulación básica con retiradas
# ==========================
st.subheader("Simulación de Ganancias y Retiradas")

if st.button("▶️ Ejecutar simulación"):
    saldo = st.session_state["saldo_inicial"]
    resultados = []

    for i in range(1, 11):  # ejemplo: 10 cuantificaciones
        # Ganancia ficticia (puedes modificar para tu % real)
        ganancia = saldo * 0.03  # 3% por cuantificación
        saldo += ganancia

        # Aplicar comisiones de referidos
        ganancia_referidos_total = 0
        for r in st.session_state["referidos"]:
            ganancia_referidos_total += ganancia * (comisiones[r["nivel"]] / 100)

        saldo_total = saldo + ganancia_referidos_total

        # Aplicar retiradas configuradas
        for retiro in st.session_state.retiros_config:
            if saldo_total >= retiro["Monto disparo"]:
                saldo_total -= retiro["Importe retiro"]

        resultados.append({
            "Cuantificación": i,
            "Saldo sin referidos (€)": round(saldo,2),
            "Ganancia por referidos (€)": round(ganancia_referidos_total,2),
            "Saldo total después de retiradas (€)": round(saldo_total,2)
        })
        saldo = saldo_total  # actualizar saldo para la siguiente cuantificación

    df_resultados = pd.DataFrame(resultados)
    st.dataframe(df_resultados, use_container_width=True)

    # Descargar CSV
    csv = df_resultados.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar resultados en CSV",
        data=csv,
        file_name="simulacion_ganancias.csv",
        mime="text/csv",
    )
