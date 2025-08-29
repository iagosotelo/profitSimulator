import streamlit as st
import pandas as pd
import io

st.title("Simulador de Ganancias en USDT (Campos numéricos libres)")

# -------------------------
# Función de conversión segura
# -------------------------
def to_float(valor, default=0.0):
    try:
        return float(valor.replace(",", "."))
    except:
        return default

# -------------------------
# Configuración principal
# -------------------------
st.subheader("Parámetros principales")
beneficio_diario_str = st.text_input("Beneficio propio diario (%)", "1")
cuantificaciones_str = st.text_input("Nº de cuantificaciones diarias", "1")
saldo_inicial_str = st.text_input("Saldo inicial (USDT)", "500")

beneficio_diario = to_float(beneficio_diario_str)
num_cuantificaciones = int(to_float(cuantificaciones_str))
saldo_inicial = to_float(saldo_inicial_str)

# -------------------------
# Configuración de retiradas
# -------------------------
st.subheader("Configuración de Retiradas")
saldo_retiro_str = st.text_input("Saldo a partir de retirada (USDT)", "500")
importe_retiro_str = st.text_input("Importe a retirar (USDT)", "100")

saldo_retiro = to_float(saldo_retiro_str)
importe_retiro = to_float(importe_retiro_str)

# -------------------------
# Referidos
# -------------------------
st.subheader("Referidos")
num_referidos_str = st.text_input("Número total de referidos", "0")
num_referidos = int(to_float(num_referidos_str))

referidos = []
for i in range(num_referidos):
    st.markdown(f"**Referido {i+1}**")
    saldo_ref_str = st.text_input(f"Saldo referido {i+1} (USDT)", "100", key=f"saldo_ref_{i}")
    nivel_str = st.selectbox(f"Nivel del referido {i+1}", ["A", "B", "C"], key=f"nivel_ref_{i}")
    saldo_ref = to_float(saldo_ref_str)
    # Definimos % por nivel
    if nivel_str == "A":
        nivel = 0.19
    elif nivel_str == "B":
        nivel = 0.07
    else:
        nivel = 0.03
    referidos.append({"saldo": saldo_ref, "nivel": nivel})

# -------------------------
# Función de simulación
# -------------------------
def simular_ganancias(saldo_inicial, beneficio_diario, num_cuantificaciones, saldo_retiro, importe_retiro, referidos):
    historial_diario = []
    historial_mensual = []

    saldo = saldo_inicial
    ganancias_totales_propias = 0
    ganancias_totales_referidos = 0

    # Diaria 90 días
    for dia in range(1, 91):
        ganancia_dia_propia = 0
        for _ in range(num_cuantificaciones):
            ganancia = saldo * beneficio_diario / 100 / num_cuantificaciones
            saldo += ganancia
            ganancia_dia_propia += ganancia
        ganancias_totales_propias += ganancia_dia_propia

        # Referidos
        ganancia_dia_ref = 0
        for ref in referidos:
            ganancia_ref = ref["saldo"] * beneficio_diario / 100
            ref["saldo"] += ganancia_ref
            ganancia_dia_ref += ganancia_ref * ref["nivel"]
        ganancias_totales_referidos += ganancia_dia_ref

        # Retirada
        if saldo >= saldo_retiro and importe_retiro > 0:
            saldo -= importe_retiro

        historial_diario.append({
            "Día": dia,
            "Saldo": round(saldo,2),
            "Ganancia propia": round(ganancias_totales_propias,2),
            "Ganancia referidos": round(ganancias_totales_referidos,2),
            "Ganancia total": round(ganancias_totales_propias + ganancias_totales_referidos,2)
        })

    # Mensual 12 meses
    saldo = saldo_inicial
    ganancias_totales_propias = 0
    ganancias_totales_referidos = 0
    for mes in range(1, 13):
        for _ in range(30):
            ganancia = saldo * beneficio_diario / 100
            saldo += ganancia
            ganancias_totales_propias += ganancia

            ganancia_ref = 0
            for ref in referidos:
                ganancia_r = ref["saldo"] * beneficio_diario / 100
                ref["saldo"] += ganancia_r
                ganancia_ref += ganancia_r * ref["nivel"]
            ganancias_totales_referidos += ganancia_ref

            if saldo >= saldo_retiro and importe_retiro > 0:
                saldo -= importe_retiro

        historial_mensual.append({
            "Mes": mes,
            "Ganancia propia": round(ganancias_totales_propias,2),
            "Ganancia referidos": round(ganancias_totales_referidos,2),
            "Ganancia total": round(ganancias_totales_propias + ganancias_totales_referidos,2)
        })

    return pd.DataFrame(historial_diario), pd.DataFrame(historial_mensual)

# -------------------------
# Ejecutar simulación
# -------------------------
if st.button("Simular"):
    df_diario, df_mensual = simular_ganancias(saldo_inicial, beneficio_diario, num_cuantificaciones, saldo_retiro, importe_retiro, referidos)

    st.subheader("Tabla diaria (90 días)")
    st.dataframe(df_diario)

    st.subheader("Tabla mensual (12 meses)")
    st.dataframe(df_mensual)

    # Exportar a Excel
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
