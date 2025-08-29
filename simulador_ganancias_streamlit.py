import streamlit as st
import pandas as pd
import io

# -------------------------
# Función de simulación
# -------------------------
def simular_ganancias(saldo_inicial, beneficio_diario, num_cuantificaciones, saldo_retiro, importe_retiro, referidos):
    historial_diario = []
    historial_mensual = []

    saldo = saldo_inicial
    ganancias_totales = 0
    ganancias_referidos = 0

    # Simulación diaria (90 días)
    for dia in range(1, 91):
        # beneficio propio
        beneficio = saldo * beneficio_diario / 100
        saldo += beneficio
        ganancias_totales += beneficio

        # ganancias de referidos
        ganancia_ref_dia = 0
        for ref in referidos:
            saldo_ref = ref["saldo"]
            benef_ref = saldo_ref * beneficio_diario / 100
            ganancia_ref_dia += benef_ref * ref["nivel"]
        ganancias_referidos += ganancia_ref_dia

        # retirada si aplica
        if saldo >= saldo_retiro:
            saldo -= importe_retiro

        historial_diario.append({
            "Día": dia,
            "Saldo": round(saldo, 2),
            "Ganancia propia": round(ganancias_totales, 2),
            "Ganancia referidos": round(ganancias_referidos, 2),
            "Ganancia total": round(ganancias_totales + ganancias_referidos, 2)
        })

    # Simulación mensual (12 meses)
    saldo = saldo_inicial
    ganancias_totales = 0
    ganancias_referidos = 0
    for mes in range(1, 13):
        for dia in range(30):  # suponemos 30 días por mes
            beneficio = saldo * beneficio_diario / 100
            saldo += beneficio
            ganancias_totales += beneficio

            ganancia_ref_dia = 0
            for ref in referidos:
                saldo_ref = ref["saldo"]
                benef_ref = saldo_ref * beneficio_diario / 100
                ganancia_ref_dia += benef_ref * ref["nivel"]
            ganancias_referidos += ganancia_ref_dia

            if saldo >= saldo_retiro:
                saldo -= importe_retiro

        historial_mensual.append({
            "Mes": mes,
            "Saldo": round(saldo, 2),
            "Ganancia propia": round(ganancias_totales, 2),
            "Ganancia referidos": round(ganancias_referidos, 2),
            "Ganancia total": round(ganancias_totales + ganancias_referidos, 2)
        })

    return pd.DataFrame(historial_diario), pd.DataFrame(historial_mensual)

# -------------------------
# Interfaz con Streamlit
# -------------------------
st.title("Simulador de Ganancias en USDT")

# Parámetros principales
beneficio_diario = st.number_input("Beneficio propio diario (%)", value=1.0)
num_cuantificaciones = st.number_input("Nº de cuantificaciones diarias", value=1, step=1)
saldo_inicial = st.number_input("Saldo inicial (USDT)", value=500)

# Configuración de retiradas
st.subheader("Configuración de retiradas")
saldo_retiro = st.number_input("Saldo a partir de retirada (USDT)", value=500)
importe_retiro = st.number_input("Importe a retirar (USDT)", value=100)

# Configuración de referidos
st.subheader("Referidos")
num_referidos = st.number_input("Nº de referidos", value=0, step=1)

referidos = []
for i in range(num_referidos):
    saldo_ref = st.number_input(f"Saldo del referido {i+1} (USDT)", value=500)
    nivel_ref = st.number_input(f"Nivel del referido {i+1}", value=1, step=1)
    referidos.append({"saldo": saldo_ref, "nivel": nivel_ref})

# Simular
if st.button("Simular"):
    df_diario, df_mensual = simular_ganancias(
        saldo_inicial, beneficio_diario, num_cuantificaciones,
        saldo_retiro, importe_retiro, referidos
    )

    st.subheader("Ganancias Diarias (90 días)")
    st.dataframe(df_diario)

    st.subheader("Ganancias Mensuales (12 meses)")
    st.dataframe(df_mensual)

    # Exportación a Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_diario.to_excel(writer, sheet_name="Diario", index=False)
        df_mensual.to_excel(writer, sheet_name="Mensual", index=False)
    st.download_button(
        label="📥 Descargar resultados en Excel",
        data=output.getvalue(),
        file_name="simulacion_ganancias.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
