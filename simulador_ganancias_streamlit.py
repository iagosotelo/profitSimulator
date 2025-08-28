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
# Referidos simplificados
# ==========================
st.subheader("Número de referidos por nivel")

if "num_referidos" not in st.session_state:
    st.session_state["num_referidos"] = {"A":0, "B":0, "C":0}

colA, colB, colC = st.columns(3)
with colA:
    try:
        st.session_state["num_referidos"]["A"] = int(st.number_input(
            "Nivel A (19%)",
            min_value=0,
            value=st.session_state["num_referidos"]["A"],
            step=1
        ))
    except:
        st.session_state["num_referidos"]["A"] = 0
with colB:
    try:
        st.session_state["num_referidos"]["B"] = int(st.number_input(
            "Nivel B (7%)",
            min_value=0,
            value=st.session_state["num_referidos"]["B"],
            step=1
        ))
    except:
        st.session_state["num_referidos"]["B"] = 0
with colC:
    try:
        st.session_state["num_referidos"]["C"] = int(st.number_input(
            "Nivel C (3%)",
            min_value=0,
            value=st.session_state["num_referidos"]["C"],
            step=1
        ))
    except:
        st.session_state["num_referidos"]["C"] = 0

comisiones = {"A": 19, "B": 7, "C": 3}

# ==========================
# Simulación de ganancias diaria y mensual
# ==========================
st.subheader("Simulación de Beneficios")

if st.button("▶️ Calcular ganancias"):
    saldo = st.session_state["saldo_inicial"]
    
    # --------------------------
    # Tabla diaria para 90 días
    # --------------------------
    dias = 90
    registros_diarios = []
    for dia in range(1, dias+1):
        ganancia_usuario = saldo * 0.03 * num_cuantificaciones
        ganancia_referidos = sum(ganancia_usuario * (comisiones[nivel]/100) * st.session_state["num_referidos"][nivel] for nivel in ["A","B","C"])
        ganancia_total = ganancia_usuario + ganancia_referidos
        
        # Aplicar retiro único
        saldo_total = saldo + ganancia_total
        if saldo_total >= retiro_disparo:
            saldo_total -= importe_retiro
        
        registros_diarios.append({
            "Día": dia,
            "Ganancia usuario (€)": round(ganancia_usuario,2),
            "Ganancia por referidos (€)": round(ganancia_referidos,2),
            "Ganancia total (€)": round(ganancia_total,2)
        })
        
        saldo = saldo_total  # actualizar saldo para siguiente día
    
    df_diario = pd.DataFrame(registros_diarios)
    st.subheader("Tabla diaria (90 días)")
    st.dataframe(df_diario, use_container_width=True)
    
    # --------------------------
    # Tabla mensual para 12 meses
    # --------------------------
    saldo = st.session_state["saldo_inicial"]
    meses = 12
    registros_mensuales = []
    for mes in range(1, meses+1):
        ganancia_usuario = saldo * 0.03 * num_cuantificaciones * 30
        ganancia_referidos = sum(ganancia_usuario * (comisiones[nivel]/100) * st.session_state["num_referidos"][nivel] for nivel in ["A","B","C"])
        ganancia_total = ganancia_usuario + ganancia_referidos
        
        # Aplicar retiro único
        saldo_total = saldo + ganancia_total
        if saldo_total >= retiro_disparo:
            saldo_total -= importe_retiro
        
        registros_mensuales.append({
            "Mes": mes,
            "Ganancia usuario (€)": round(ganancia_usuario,2),
            "Ganancia por referidos (€)": round(ganancia_referidos,2),
            "Ganancia total (€)": round(ganancia_total,2)
        })
        
        saldo = saldo_total  # actualizar saldo para siguiente mes
    
    df_mensual = pd.DataFrame(registros_mensuales)
    st.subheader("Tabla mensual (12 meses)")
    st.dataframe(df_mensual, use_container_width=True)
    
    # --------------------------
    # Descargar CSV
    # --------------------------
    csv_diario = df_diario.to_csv(index=False).encode("utf-8")
    csv_mensual = df_mensual.to_csv(index=False).encode("utf-8")
    
    st.download_button(
        label="📥 Descargar resultados diarios CSV",
        data=csv_diario,
        file_name="simulacion_diaria.csv",
        mime="text/csv"
    )
    
    st.download_button(
        label="📥 Descargar resultados mensuales CSV",
        data=csv_mensual,
        file_name="simulacion_mensual.csv",
        mime="text/csv"
    )
