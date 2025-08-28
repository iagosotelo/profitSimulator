# Archivo: simulador_ganancias.py
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Simulador de ganancias App", layout="wide")
st.title("Simulador de ganancias con 3 niveles de referidos")

# -------------------------------
# Parámetros de usuario preconfigurados
# -------------------------------
saldo_usuario = st.number_input("Saldo inicial usuario (€):", value=287.10)
ganancia_diaria_total = st.number_input("Ganancia diaria total (€):", value=5.10)
cuantificaciones_diarias = st.number_input("Cuantificaciones diarias:", value=4, min_value=1)
umbral_retiro = st.number_input("Umbral de retiro (€):", value=450.0)
monto_retiro = st.number_input("Monto de retiro (€):", value=100.0)
dias_a_simular = st.number_input("Días a simular:", value=365)

tasa_diaria_total = ganancia_diaria_total / saldo_usuario
tasa_por_cuantificacion = tasa_diaria_total / cuantificaciones_diarias

# -------------------------------
# Árbol de referidos preconfigurado
# -------------------------------
st.subheader("Referidos preconfigurados")
nivelA_saldo = st.number_input("Saldo referido Nivel A (€):", value=185.89)
nivelB_saldo = st.number_input("Saldo referido Nivel B (€):", value=100.0)
nivelC_saldo = st.number_input("Saldo referido Nivel C (€):", value=50.0)

referidos = [
    {"saldo": nivelA_saldo, "nivel": "A", "comision": 0.19, "sub_referidos": [
        {"saldo": nivelB_saldo, "nivel": "B", "comision": 0.07, "sub_referidos": [
            {"saldo": nivelC_saldo, "nivel": "C", "comision": 0.03, "sub_referidos": []}
        ]}
    ]}
]

# -------------------------------
# Función recursiva para referidos
# -------------------------------
def actualizar_referidos(ref_list, saldo_usuario, tasa_cuant):
    comision_total = 0.0
    for ref in ref_list:
        ganancia_ref = ref["saldo"] * tasa_cuant
        ref["saldo"] += ganancia_ref
        comision = ganancia_ref * ref["comision"]
        saldo_usuario += comision
        comision_total += comision
        while ref["saldo"] >= umbral_retiro:
            ref["saldo"] -= monto_retiro
        if ref["sub_referidos"]:
            comision_total += actualizar_referidos(ref["sub_referidos"], saldo_usuario, tasa_cuant)
    return comision_total

# -------------------------------
# Simulación diaria
# -------------------------------
registros = []
comision_acumulada = 0.0

for dia in range(dias_a_simular + 1):
    ganancia_dia_total = 0.0
    for q in range(cuantificaciones_diarias):
        ganancia_usuario = saldo_usuario * tasa_por_cuantificacion
        saldo_usuario += ganancia_usuario
        ganancia_dia_total += ganancia_usuario

        comision = actualizar_referidos(referidos, saldo_usuario, tasa_por_cuantificacion)
        saldo_usuario += comision
        comision_acumulada += comision

        while saldo_usuario >= umbral_retiro:
            saldo_usuario -= monto_retiro

    registro = {
        "día": dia,
        "saldo_usuario": round(saldo_usuario, 2),
        "ganancia_usuario_dia": round(ganancia_dia_total, 2),
        "comision_acumulada": round(comision_acumulada, 2),
        "saldos_referidos": [round(r["saldo"], 2) for r in referidos]
    }
    registros.append(registro)

df = pd.DataFrame(registros)
df["mes"] = df["día"] // 30 + 1
resumen_mensual = df.groupby("mes").agg({
    "saldo_usuario": "last",
    "ganancia_usuario_dia": "sum",
    "comision_acumulada": "last"
}).reset_index()

# -------------------------------
# Mostrar tablas
# -------------------------------
st.subheader("Tabla diaria (primeros 30 días)")
st.dataframe(df.head(30))

st.subheader("Resumen mensual")
st.dataframe(resumen_mensual)

# Botones para exportar CSV
st.download_button(
    label="Descargar datos diarios CSV",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name="ganancias_diarias.csv",
    mime="text/csv"
)

st.download_button(
    label="Descargar resumen mensual CSV",
    data=resumen_mensual.to_csv(index=False).encode('utf-8'),
    file_name="resumen_mensual.csv",
    mime="text/csv"
)

# -------------------------------
# Gráficos con Plotly
# -------------------------------
st.subheader("Gráficos de evolución")
fig = px.line(df, x="día", y="saldo_usuario", title="Saldo Usuario", labels={"día": "Día", "saldo_usuario": "Saldo (€)"})
fig.add_scatter(x=df["día"], y=df["comision_acumulada"], mode='lines', name='Comisiones acumuladas')
for i, r in enumerate(referidos):
    fig.add_scatter(x=df["día"], y=[s[i] for s in df["saldos_referidos"]], mode='lines', name=f"Saldo referido nivel {r['nivel']}")
st.plotly_chart(fig, use_container_width=True)
