import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Ganancias USDT", layout="wide")
st.title("💰 Simulador de Ganancias Diarias con Referidos y Retiradas (USDT)")

# ==========================
# Saldo inicial
# ==========================
if "saldo_inicial" not in st.session_state:
    st.session_state["saldo_inicial"] = 0.0

saldo_input = st.text_input(
    "Saldo inicial del usuario (USDT)",
    value=str(st.session_state["saldo_inicial"])
)
try:
    st.session_state["saldo_inicial"] = float(saldo_input.replace(',', '.'))
except:
    st.warning("Introduce un número válido para el saldo inicial")

# ==========================
# Configuración de retiradas
# ==========================
st.subheader("Configuración de retiradas periódicas")

saldo_limite_input = st.text_input(
    "Saldo límite para operar (USDT, solo referencia)",
    value="500"
)
try:
    saldo_limite = float(saldo_limite_input.replace(',', '.'))
except:
    saldo_limite = 500.0

saldo_retiro_input = st.text_input(
    "Saldo a partir del cual se realiza la retirada (USDT)",
    value="0"
)
try:
    saldo_retiro = float(saldo_retiro_input.replace(',', '.'))
except:
    saldo_retiro = 0.0

importe_retiro_input = st.text_input(
    "Importe a retirar cuando se alcanza el saldo de retirada (USDT)",
    value="0"
)
try:
    importe_retiro = float(importe_retiro_input.replace(',', '.'))
except:
    importe_retiro = 0.0

# ==========================
# Cuantificaciones y beneficio diario
# ==========================
num_cuantificaciones = st.number_input(
    "Número de cuantificaciones diarias",
    min_value=1,
    value=4,
    step=1
)

porcentaje_beneficio_diario = st.number_input(
    "Beneficio propio diario (%)",
    min_value=0.0,
    value=3.0,
    step=0.1
)

# ==========================
# Referidos simplificados
# ==========================
st.subheader("Número de referidos por nivel")
if "num_referidos" not in st.session_state:
    st.session_state["num_referidos"] = {"A":0, "B":0, "C":0}

colA, colB, colC = st.columns(3)
with colA:
    st.session_state["num_referidos"]["A"] = st.number_input(
        "Nivel A (19%)",
        min_value=0,
        value=st.session_state["num_referidos"]["A"],
        step=1
    )
with colB:
    st.session_state["num_referidos"]["B"] = st.number_input(
        "Nivel B (7%)",
        min_value=0,
        value=st.session_state["num_referidos"]["B"],
        step=1
    )
with colC:
    st.session_state["num_referidos"]["C"] = st.number_input(
        "Nivel C (3%)",
        min_value=0,
        value=st.session_state["num_referidos"]["C"],
        step=1
    )

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
        saldo_dia = saldo
        ganancia_usuario_total = 0
        ganancia_referidos_total = 0
        
        # Operar por cuantificaciones
        for _ in range(num_cuantificaciones):
            ganancia_usuario = saldo_dia * (porcentaje_beneficio_diario / 100) / num_cuantificaciones
            ganancia_referidos = sum(
                ganancia_usuario * (comisiones[nivel]/100) * st.session_state["num_referidos"][nivel]
                for nivel in ["A","B","C"]
            )
            saldo_dia += ganancia_usuario + ganancia_referidos
            ganancia_usuario_total += ganancia_usuario
            ganancia_referidos_total += ganancia_referidos
        
        # Retirada al final del día si se alcanza saldo_retiro
        if saldo_dia >= saldo_retiro:
            saldo_dia -= importe_retiro
        
        registros_diarios.append({
            "Día": dia,
            "Ganancia usuario (USDT)": round(ganancia_usuario_total,2),
            "Ganancia por referidos (USDT)": round(ganancia_referidos_total,2),
            "Ganancia total (USDT)": round(ganancia_usuario_total + ganancia_referidos_total,2)
        })
        
        saldo = saldo_dia  # saldo del siguiente día
    
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
        saldo_mes = saldo
        ganancia_usuario_total = 0
        ganancia_referidos_total = 0
        # Aproximar mes a 30 días, operando cada día con cuantificaciones
        for _ in range(30):
            saldo_dia = saldo_mes
            ganancia_usuario_dia = 0
            ganancia_referidos_dia = 0
            for _ in range(num_cuantificaciones):
                g_usuario = saldo_dia * (porcentaje_beneficio_diario / 100) / num_cuantificaciones
                g_referidos = sum(
                    g_usuario * (comisiones[nivel]/100) * st.session_state["num_referidos"][nivel]
                    for nivel in ["A","B","C"]
                )
                saldo_dia += g_usuario + g_referidos
                ganancia_usuario_dia += g_usuario
                ganancia_referidos_dia += g_referidos
            # Retirada al final del día
            if saldo_dia >= saldo_retiro:
                saldo_dia -= importe_retiro
            saldo_mes = saldo_dia
            ganancia_usuario_total += ganancia_usuario_dia
            ganancia_referidos_total += ganancia_referidos_dia
        
        registros_mensuales.append({
            "Mes": mes,
            "Ganancia usuario (USDT)": round(ganancia_usuario_total,2),
            "Ganancia por referidos (USDT)": round(ganancia_referidos_total,2),
            "Ganancia total (USDT)": round(ganancia_usuario_total + ganancia_referidos_total,2)
        })
        
        saldo = saldo_mes
    
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
