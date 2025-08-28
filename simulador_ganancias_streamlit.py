# Archivo: simulador\_ganancias.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página

st.set\_page\_config(page\_title="Simulador de ganancias App", layout="wide")
st.title("Simulador de ganancias con 3 niveles de referidos")

# -------------------------------

# Parámetros de usuario preconfigurados

# -------------------------------

saldo\_usuario = st.number\_input("Saldo inicial usuario (€):", value=287.10)
ganancia\_diaria\_total = st.number\_input("Ganancia diaria total (€):", value=5.10)
cuantificaciones\_diarias = st.number\_input("Cuantificaciones diarias:", value=4, min\_value=1)
umbral\_retiro = st.number\_input("Umbral de retiro (€):", value=450.0)
monto\_retiro = st.number\_input("Monto de retiro (€):", value=100.0)
dias\_a\_simular = st.number\_input("Días a simular:", value=365)

tasa\_diaria\_total = ganancia\_diaria\_total / saldo\_usuario
tasa\_por\_cuantificacion = tasa\_diaria\_total / cuantificaciones\_diarias

# -------------------------------

# Árbol de referidos preconfigurado

# -------------------------------

st.subheader("Referidos preconfigurados")
nivelA\_saldo = st.number\_input("Saldo referido Nivel A (€):", value=185.89)
nivelB\_saldo = st.number\_input("Saldo referido Nivel B (€):", value=100.0)
nivelC\_saldo = st.number\_input("Saldo referido Nivel C (€):", value=50.0)

referidos = \[
{"saldo": nivelA\_saldo, "nivel": "A", "comision": 0.19, "sub\_referidos": \[
{"saldo": nivelB\_saldo, "nivel": "B", "comision": 0.07, "sub\_referidos": \[
{"saldo": nivelC\_saldo, "nivel": "C", "comision": 0.03, "sub\_referidos": \[]}
]}
]}
]

# -------------------------------

# Función recursiva para referidos

# -------------------------------

def actualizar\_referidos(ref\_list, saldo\_usuario, tasa\_cuant):
comision\_total = 0.0
for ref in ref\_list:
ganancia\_ref = ref\["saldo"] \* tasa\_cuant
ref\["saldo"] += ganancia\_ref
comision = ganancia\_ref \* ref\["comision"]
saldo\_usuario += comision
comision\_total += comision
while ref\["saldo"] >= umbral\_retiro:
ref\["saldo"] -= monto\_retiro
if ref\["sub\_referidos"]:
comision\_total += actualizar\_referidos(ref\["sub\_referidos"], saldo\_usuario, tasa\_cuant)
return comision\_total

# -------------------------------

# Simulación diaria

# -------------------------------

registros = \[]
comision\_acumulada = 0.0

for dia in range(dias\_a\_simular + 1):
ganancia\_dia\_total = 0.0
for q in range(cuantificaciones\_diarias):
ganancia\_usuario = saldo\_usuario \* tasa\_por\_cuantificacion
saldo\_usuario += ganancia\_usuario
ganancia\_dia\_total += ganancia\_usuario

```
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
```

df = pd.DataFrame(registros)
df\["mes"] = df\["día"] // 30 + 1
resumen\_mensual = df.groupby("mes").agg({
"saldo\_usuario": "last",
"ganancia\_usuario\_dia": "sum",
"comision\_acumulada": "last"
}).reset\_index()

# -------------------------------

# Mostrar tablas

# -------------------------------

st.subheader("Tabla diaria (primeros 30 días)")
st.dataframe(df.head(30))

st.subheader("Resumen mensual")
st.dataframe(resumen\_mensual)

# Botones para exportar CSV

st.download\_button(
label="Descargar datos diarios CSV",
data=df.to\_csv(index=False).encode('utf-8'),
file\_name="ganancias\_diarias.csv",
mime="text/csv"
)

st.download\_button(
label="Descargar resumen mensual CSV",
data=resumen\_mensual.to\_csv(index=False).encode('utf-8'),
file\_name="resumen\_mensual.csv",
mime="text/csv"
)

# -------------------------------

# Gráficos con Plotly

# -------------------------------

st.subheader("Gráficos de evolución")
fig = px.line(df, x="día", y="saldo\_usuario", title="Saldo Usuario", labels={"día": "Día", "saldo\_usuario": "Saldo (€)"})
fig.add\_scatter(x=df\["día"], y=df\["comision\_acumulada"], mode='lines', name='Comisiones acumuladas')
for i, r in enumerate(referidos):
fig.add\_scatter(x=df\["día"], y=\[s\[i] for s in df\["saldos\_referidos"]], mode='lines', name=f"Saldo referido nivel {r\['nivel']}")
st.plotly\_chart(fig, use\_container\_width=True)
