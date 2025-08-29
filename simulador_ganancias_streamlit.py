import streamlit as st
import pandas as pd
import io
from openpyxl import Workbook

st.title("Simulador de Ganancias (USDT)")

# ===============================
# Configuración principal
# ===============================
cuantificaciones_diarias = st.number_input("Nº de cuantificaciones diarias", min_value=1, value=1, step=1)
beneficio_propio_diario = st.number_input("Beneficio propio diario (%)", min_value=0.0, value=1.0, step=0.1)

# ===============================
# Configuración de retiradas
# ===============================
st.subheader("Configuración de Retiradas")
saldo_retirada = st.number_input("Saldo a partir del cual retirar (USDT)", min_value=0.0, value=500.0, step=1.0)
importe_retirada = st.number_input("Importe a retirar (USDT)", min_value=0.0, value=100.0, step=1.0)

# ===============================
# Referidos
# ===============================
st.subheader("Gestión de Referidos")

referidos = []
n_referidos = st.number_input("Número total de referidos", min_value=0, value=0, step=1)

for i in range(n_referidos):
    st.markdown(f"### Referido {i+1}")
    saldo_inicial = st.number_input(f"Saldo inicial referido {i+1} (USDT)", min_value=0.0, value=100.0, step=1.0)
    nivel = st.selectbox(f"Nivel del referido {i+1}", ["A", "B", "C"], index=0, key=f"nivel_{i}")
    referidos.append({"saldo": saldo_inicial, "nivel": nivel})

# Porcentajes por nivel
porcentajes_nivel = {"A": 0.20, "B": 0.10, "C": 0.05}

# ===============================
# Simulación
# ===============================
st.subheader("Resultados de la Simulación")

saldo_inicial = st.number_input("Saldo inicial propio (USDT)", min_value=0.0, value=500.0, step=1.0)

dias = 90
meses = 12

resultados_dia = []
resultados_mes = []

saldo = saldo_inicial
saldos_referidos = [r["saldo"] for r in referidos]

ganancia_total_propia = 0
ganancia_total_referidos = 0

for dia in range(1, dias + 1):
    ganancia_dia_propia = 0
    saldo_dia = saldo
    for _ in range(cuantificaciones_diarias):
        ganancia_cuantificacion = saldo_dia * (beneficio_propio_diario / 100) / cuantificaciones_diarias
        saldo_dia += ganancia_cuantificacion
        ganancia_dia_propia += ganancia_cuantificacion

    # Aplicar retiro si aplica
    if saldo_dia >= saldo_retirada and importe_retirada > 0:
        saldo_dia -= importe_retirada

    saldo = saldo_dia
    ganancia_total_propia += ganancia_dia_propia

    # Ganancia por referidos
    ganancia_dia_referidos = 0
    for i, ref in enumerate(referidos):
        saldo_ref = saldos_referidos[i]
        ganancia_ref_dia = 0
        saldo_ref_dia = saldo_ref
        for _ in range(cuantificaciones_diarias):
            g_ref = saldo_ref_dia * (beneficio_propio_diario / 100) / cuantificaciones_diarias
            saldo_ref_dia += g_ref
            ganancia_ref_dia += g_ref
        # Aplicar retiro en referidos
        if saldo_ref_dia >= saldo_retirada and importe_retirada > 0:
            saldo_ref_dia -= importe_retirada
        saldos_referidos[i] = saldo_ref_dia
        ganancia_dia_referidos += ganancia_ref_dia * porcentajes_nivel[ref["nivel"]]

    ganancia_total_referidos += ganancia_dia_referidos

    resultados_dia.append({
        "Día": dia,
        "Saldo Propio (USDT)": round(saldo, 2),
        "Ganancia Propia (USDT)": round(ganancia_total_propia, 2),
        "Ganancia Referidos (USDT)": round(ganancia_total_referidos, 2),
        "Ganancia Total (USDT)": round(ganancia_total_propia + ganancia_total_referidos, 2),
    })

# Resumen mensual
for mes in range(1, meses + 1):
    dias_mes = mes * 30
    if dias_mes <= len(resultados_dia):
        fila = resultados_dia[dias_mes - 1]
        resultados_mes.append({
            "Mes": mes,
            "Ganancia Propia (USDT)": fila["Ganancia Propia (USDT)"],
            "Ganancia Referidos (USDT)": fila["Ganancia Referidos (USDT)"],
            "Ganancia Total (USDT)": fila["Ganancia Total (USDT)"],
        })

df_dias = pd.DataFrame(resultados_dia)
df_meses = pd.DataFrame(resultados_mes)

st.markdown("### Tabla Diaria (90 días)")
st.dataframe(df_dias)

st.markdown("### Tabla Mensual (12 meses)")
st.dataframe(df_meses)

# ===============================
# Exportar a Excel
# ===============================
output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_dias.to_excel(writer, sheet_name="Diario", index=False)
    df_meses.to_excel(writer, sheet_name="Mensual", index=False)
excel_data = output.getvalue()

st.download_button(
    label="📥 Descargar resultados en Excel",
    data=excel_data,
    file_name="simulacion_ganancias.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
