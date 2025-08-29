import streamlit as st
import pandas as pd

# -------------------------
# Simulación de ganancias
# -------------------------
def simular_ganancias(saldo_inicial, beneficio_diario, cuantificaciones, saldo_retiro, importe_retiro, referidos):
    saldo = saldo_inicial
    historial_diario = []
    historial_mensual = []
    ganancia_total = 0

    # Simulación diaria (90 días)
    for dia in range(1, 91):
        # aplicar beneficio diario
        beneficio = saldo * (beneficio_diario / 100)
        saldo += beneficio

        # sumar ganancias por referidos
        ganancia_referidos = 0
        for ref in referidos:
            saldo_ref = ref["saldo"]
            nivel = ref["nivel"]
            if nivel == "A":
                porcentaje = 0.12
            elif nivel == "B":
                porcentaje = 0.08
            else:  # nivel C
                porcentaje = 0.05

            beneficio_ref = saldo_ref * (beneficio_diario / 100)
            ganancia_ref = beneficio_ref * porcentaje
            saldo_ref += beneficio_ref
            ref["saldo"] = saldo_ref
            ganancia_referidos += ganancia_ref

        ganancia_total += beneficio + ganancia_referidos

        # comprobación de retiro
        if saldo >= saldo_retiro:
            saldo -= importe_retiro

        historial_diario.append({
            "Día": dia,
            "Saldo": round(saldo, 2),
            "Ganancia propia": round(beneficio, 2),
            "Ganancia referidos": round(ganancia_referidos, 2),
            "Ganancia total": round(ganancia_total, 2)
        })

    # Simulación mensual (12 meses)
    saldo = saldo_inicial
    ganancia_total = 0
    for mes in range(1, 13):
        ganancia_mes = 0
        ganancia_ref_mes = 0

        for dia in range(30):
            beneficio = saldo * (beneficio_diario / 100)
            saldo += beneficio
            ganancia_mes += beneficio

            ganancia_referidos = 0
            for ref in referidos:
                saldo_ref = ref["saldo"]
                nivel = ref["nivel"]
                if nivel == "A":
                    porcentaje = 0.12
                elif nivel == "B":
                    porcentaje = 0.08
                else:
                    porcentaje = 0.05

                beneficio_ref = saldo_ref * (beneficio_diario / 100)
                ganancia_ref = beneficio_ref * porcentaje
                saldo_ref += beneficio_ref
                ref["saldo"] = saldo_ref
                ganancia_referidos += ganancia_ref

            ganancia_ref_mes += ganancia_referidos

            if saldo >= saldo_retiro:
                saldo -= importe_retiro

        ganancia_total += ganancia_mes + ganancia_ref_mes
        historial_mensual.append({
            "Mes": mes,
            "Saldo": round(saldo, 2),
            "Ganancia propia": round(ganancia_mes, 2),
            "Ganancia referidos": round(ganancia_ref_mes, 2),
            "Ganancia total": round(ganancia_total, 2)
        })

    return historial_diario, historial_mensual


# -------------------------
# Interfaz Streamlit
# -------------------------
st.title("Simulador de ganancias en USDT")

# Parámetros principales
st.subheader("Parámetros principales")
saldo_inicial = st.number_input("Saldo inicial (USDT)", min_value=0.0, value=500.0, step=10.0, key="saldo_inicial")
beneficio_diario = st.number_input("Beneficio propio diario (%)", min_value=0.0, value=1.0, step=0.1, key="beneficio_diario")
cuantificaciones = st.number_input("Nº de cuantificaciones diarias", min_value=1, value=1, step=1, key="cuantificaciones")

# Configuración de retiradas
st.subheader("Configuración de retiradas")
saldo_retiro = st.number_input("Saldo a partir de retirada (USDT)", min_value=0.0, value=500.0, step=10.0, key="saldo_retiro")
importe_retiro = st.number_input("Importe a retirar (USDT)", min_value=0.0, value=100.0, step=10.0, key="importe_retiro")

# Gestión de referidos
st.subheader("Referidos")
num_referidos = st.number_input("Número total de referidos", min_value=0, value=0, step=1, key="num_referidos")
referidos = []
for i in range(num_referidos):
    st.markdown(f"**Referido {i+1}**")
    saldo_ref = st.number_input(f"Saldo referido {i+1}", min_value=0.0, value=100.0, step=10.0, key=f"saldo_ref_{i}")
    nivel_ref = st.selectbox(f"Nivel referido {i+1}", ["A", "B", "C"], key=f"nivel_ref_{i}")
    referidos.append({"saldo": saldo_ref, "nivel": nivel_ref})

# Ejecutar simulación
if st.button("Simular"):
    diario, mensual = simular_ganancias(saldo_inicial, beneficio_diario, cuantificaciones, saldo_retiro, importe_retiro, referidos)

    st.subheader("Resultados diarios (90 días)")
    df_diario = pd.DataFrame(diario)
    st.dataframe(df_diario)

    st.subheader("Resultados mensuales (12 meses)")
    df_mensual = pd.DataFrame(mensual)
    st.dataframe(df_mensual)
