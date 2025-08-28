import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Ganancias App", layout="wide")
st.title("💰 Simulador de Ganancias con Referidos y Retiro Único")

# ==========================
# Saldo inicial
# ==========================
if "saldo_inicial" not in st.session_state:
    st.session_state["saldo_inicial"] = 0.0

saldo_input = st.text_input(
    "Saldo inicial del usuario (€)",
    value=str(st.session_state["saldo_inicial"])
)
try:
    st.session_state["saldo_inicial"] = float(saldo_input.replace(',', '.'))
except:
    st.warning("Introduce un número válido para el saldo inicial")

# ==========================
# Configuración de retiro
# ==========================
st.subheader("Retiro único")

retiro_disparo_input = st.text_input(
    "Saldo a partir del cual se realiza la retirada (€)",
    value="0"
)
try:
    retiro_disparo = float(retiro_disparo_input.replace(',', '.'))
except:
    retiro_disparo = 0.0
    st.warning("Introduce un número válido para saldo disparo")

importe_retiro_input = st.text_input(
    "Importe a retirar (€)",
    value="0"
)
try:
    importe_retiro = float(importe_retiro_input.replace(',', '.'))
except:
    importe_retiro = 0.0
    st.warning("Introduce un número válido para importe a retirar")

# ==========================
# Número de cuantificaciones
# ==========================
num_cuantificaciones = st.number_input(
    "Número de cuantificaciones diarias",
    min_value=1,
    value=4,
    step=1
)

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
for i, ref in enumerate(st.session_state["referidos"]):
    cols = st.columns([2,1,1])
    with cols[0]:
        nombre = st.text_input(f"Nombre referido {i+1}", value=ref["nombre"], key=f"nombre_{i}")
    with cols[1]:
        nivel = st.selectbox(f"Nivel {i+1}", ["A","B","C"], index=["A","B","C"].index(ref["nivel"]), key=f"nivel_{i}")
    with cols[2]:
        st.write(f"Comisión: {comisiones[nivel]}%")
    nuevos_referidos.append({"nombre": nombre, "nivel": nivel})

st.session_state.referidos = nuevos_referidos

# ==========================
# Simulación de ganancias
# ==========================
st.subheader("Simulación de Beneficios Totales")

if st.button("▶️ Calcular ganancias"):
    saldo = st.session_state["saldo_inicial"]
    
    # Ganancia diaria del usuario (por ejemplo, 3% diaria)
    ganancia_usuario_total = saldo * 0.03 * num_cuantificaciones
    
    # Comisiones de referidos
    ganancia_referidos_total = 0
    for r in st.session_state["referidos"]:
        ganancia_referidos_total += ganancia_usuario_total * (comisiones[r["nivel"]] / 100)
    
    saldo_total = saldo + ganancia_usuario_total + ganancia_referidos_total
    
    # Aplicar retiro si se alcanza el monto
    if saldo_total >= retiro_disparo:
        saldo_total -= importe_retiro
    
    # Crear tabla final
    df_resultado = pd.DataFrame([{
        "Saldo inicial (€)": round(saldo,2),
        f"Ganancia usuario ({num_cuantificaciones} cuantificaciones) (€)": round(ganancia_usuario_total,2),
        "Ganancia por referidos (€)": round(ganancia_referidos_total,2),
        "Saldo final después de retiro (€)": round(saldo_total,2)
    }])
    
    st.dataframe(df_resultado, use_container_width=True)
    
    # Descargar CSV
    csv = df_resultado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar resultados en CSV",
        data=csv,
        file_name="simulacion_ganancias.csv",
        mime="text/csv"
    )
