import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Simulador de ganancias App", layout="wide")

st.title("📈 Simulador de Ganancias")

# Entrada de datos
col1, col2, col3 = st.columns(3)

with col1:
    saldo_inicial = st.number_input("Saldo inicial (€)", min_value=0.0, value=0.0, step=10.0)
    rendimiento = st.number_input("Rendimiento por cuantificación (%)", min_value=0.0, value=3.0, step=0.1)

with col2:
    num_cuantificaciones = st.number_input("Número de cuantificaciones", min_value=1, value=4, step=1)
    comision_referido = st.number_input("Comisión por referido (%)", min_value=0.0, value=19.0, step=0.1)

with col3:
    num_referidos = st.number_input("Número de referidos", min_value=0, value=0, step=1)


# Función para simular
def simular_ganancias(saldo_inicial, rendimiento, num_cuantificaciones, comision_referido, num_referidos):
    resultados = []
    saldo = saldo_inicial

    for i in range(1, num_cuantificaciones + 1):
        ganancia = saldo * (rendimiento / 100)
        saldo += ganancia

        # Ganancia de referidos
        ganancia_referidos = (ganancia * (comision_referido / 100)) * num_referidos
        saldo_total = saldo + ganancia_referidos

        resultados.append({
            "Cuantificación": i,
            "Saldo sin referidos (€)": round(saldo, 2),
            "Ganancia por referidos (€)": round(ganancia_referidos, 2),
            "Saldo total (€)": round(saldo_total, 2)
        })

    return pd.DataFrame(resultados)


# Ejecutar simulación
if st.button("Simular"):
    df = simular_ganancias(saldo_inicial, rendimiento, num_cuantificaciones, comision_referido, num_referidos)

    st.subheader("📊 Resultados de la simulación")
    st.dataframe(df, use_container_width=True)

    saldo_final = df["Saldo total (€)"].iloc[-1]
    st.metric("💰 Saldo final del usuario", f"{saldo_final:.2f} €")

    # Botón de descarga CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar resultados en CSV",
        data=csv,
        file_name="simulacion_ganancias.csv",
        mime="text/csv",
    )

    # Botón de descarga Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    processed_data = output.getvalue()

    st.download_button(
        label="📥 Descargar resultados en Excel",
        data=processed_data,
        file_name="simulacion_ganancias.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
