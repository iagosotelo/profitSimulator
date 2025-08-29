# simulador_ganancias_streamlit.py (Streamlit)
# Ejecuta: streamlit run simulador_ganancias_streamlit.py

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Ganancias USDT", layout="wide")
st.title("💰 Simulador de Ganancias con Referidos y Retiradas (USDT)")

# -------------------------------
# Helpers
# -------------------------------
def parse_float(txt: str, default: float = 0.0) -> float:
    try:
        txt = (txt or "").strip().replace(" ", "").replace(",", ".")
        if txt == "":
            return default
        return float(txt)
    except Exception:
        return default

def parse_int(txt: str, default: int = 1) -> int:
    try:
        txt = (txt or "").strip().replace(" ", "").replace(",", ".")
        if txt == "":
            return default
        # Acepta números escritos como "4", "4.0", etc.
        return int(float(txt))
    except Exception:
        return default

def operar_un_dia(saldo_inicial: float, pct_diario: float, cuantificaciones: int):
    """
    Aplica el beneficio diario en 'cuantificaciones' partes.
    Devuelve (saldo_final_del_dia, ganancia_dia).
    """
    saldo = saldo_inicial
    ganancia = 0.0
    if cuantificaciones < 1:
        cuantificaciones = 1
    for _ in range(cuantificaciones):
        g = saldo * (pct_diario / 100.0) / cuantificaciones
        saldo += g
        ganancia += g
    return saldo, ganancia

# -------------------------------
# Parámetros de operación
# -------------------------------
st.subheader("Parámetros de operación")

# Nº de cuantificaciones (texto para permitir libre edición)
if "num_cuantificaciones_txt" not in st.session_state:
    st.session_state["num_cuantificaciones_txt"] = "4"
num_cuantificaciones_txt = st.text_input(
    "Número de cuantificaciones diarias",
    value=st.session_state["num_cuantificaciones_txt"],
    help="Se reparte el beneficio diario en ese número de operaciones."
)
st.session_state["num_cuantificaciones_txt"] = num_cuantificaciones_txt
num_cuantificaciones = parse_int(num_cuantificaciones_txt, default=4)
if num_cuantificaciones < 1:
    num_cuantificaciones = 1

# Beneficio propio diario % (texto para permitir coma/decimal)
if "beneficio_diario_txt" not in st.session_state:
    st.session_state["beneficio_diario_txt"] = "1.0"
beneficio_diario_txt = st.text_input(
    "Beneficio propio diario (%)",
    value=st.session_state["beneficio_diario_txt"],
    help="Porcentaje diario. Ej.: 1,7 significa 1.7% al día."
)
st.session_state["beneficio_diario_txt"] = beneficio_diario_txt
porcentaje_beneficio_diario = parse_float(beneficio_diario_txt, default=1.0)
if porcentaje_beneficio_diario < 0:
    porcentaje_beneficio_diario = 0.0

# Saldo inicial (texto para permitir coma/decimal). Debe iniciar en 0.
if "saldo_inicial_txt" not in st.session_state:
    st.session_state["saldo_inicial_txt"] = "0"
saldo_inicial_txt = st.text_input(
    "Saldo inicial del usuario (USDT)",
    value=st.session_state["saldo_inicial_txt"]
)
st.session_state["saldo_inicial_txt"] = saldo_inicial_txt
saldo_inicial = parse_float(saldo_inicial_txt, default=0.0)
if saldo_inicial < 0:
    saldo_inicial = 0.0

# -------------------------------
# Configuración de retiradas
# -------------------------------
st.subheader("Configuración de retiradas periódicas")

if "saldo_retiro_txt" not in st.session_state:
    st.session_state["saldo_retiro_txt"] = "500"
saldo_retiro_txt = st.text_input(
    "Saldo a partir del cual se realiza la retirada (USDT)",
    value=st.session_state["saldo_retiro_txt"],
    help="Cuando el saldo al final del día alcance o supere este valor, se retira el importe configurado."
)
st.session_state["saldo_retiro_txt"] = saldo_retiro_txt
saldo_retiro = parse_float(saldo_retiro_txt, default=500.0)

if "importe_retiro_txt" not in st.session_state:
    st.session_state["importe_retiro_txt"] = "100"
importe_retiro_txt = st.text_input(
    "Importe a retirar cuando se alcanza el saldo de retirada (USDT)",
    value=st.session_state["importe_retiro_txt"]
)
st.session_state["importe_retiro_txt"] = importe_retiro_txt
importe_retiro = parse_float(importe_retiro_txt, default=100.0)
if importe_retiro < 0:
    importe_retiro = 0.0

# -------------------------------
# Gestión de referidos
# -------------------------------
st.subheader("Gestión de referidos (saldo y nivel)")

if "referidos" not in st.session_state:
    st.session_state["referidos"] = []  # cada elem: {"nivel": "A|B|C", "saldo": float}

with st.expander("➕ Añadir referido"):
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        nivel_nuevo = st.selectbox("Nivel", ["A", "B", "C"], index=0, key="nivel_nuevo")
    with col2:
        saldo_nuevo_txt = st.text_input("Saldo del referido (USDT)", value="0", key="saldo_nuevo_txt")
    with col3:
        if st.button("Añadir", use_container_width=True):
            saldo_nuevo = parse_float(saldo_nuevo_txt, default=0.0)
            if saldo_nuevo < 0:
                saldo_nuevo = 0.0
            st.session_state["referidos"].append({"nivel": nivel_nuevo, "saldo": saldo_nuevo})
            st.success("Referido añadido")

# Mostrar y permitir eliminar
if st.session_state["referidos"]:
    df_ref = pd.DataFrame([
        {"Nivel": r["nivel"], "Saldo (USDT)": round(float(r["saldo"]), 6)}
        for r in st.session_state["referidos"]
    ])
    st.dataframe(df_ref, use_container_width=True)
    idx_del = st.number_input("Eliminar referido (índice, empezando en 0)", min_value=0, max_value=len(st.session_state["referidos"])-1, value=0, step=1)
    if st.button("Eliminar referido seleccionado"):
        st.session_state["referidos"].pop(int(idx_del))
        st.success("Referido eliminado")

# Comisiones por nivel (en %)
COMISIONES = {"A": 19.0, "B": 7.0, "C": 3.0}

# -------------------------------
# Simulación
# -------------------------------
st.subheader("Simulación de Beneficios")

def simular_periodo(dias: int, saldo_usuario_inicial: float, referidos_iniciales: list):
    """
    Simula 'dias' días, aplicando:
      - beneficio diario dividido en N cuantificaciones
      - retirada al final del día si el saldo >= saldo_retiro
      - referidos con misma lógica (su saldo crece y también se someten a retiradas)
    Retorna:
      - registros_diarios: lista de dicts con resultados del día
      - saldo_usuario_final, referidos_finales
    """
    saldo_usuario = float(saldo_usuario_inicial)
    referidos_sim = [{"nivel": r["nivel"], "saldo": float(r["saldo"])} for r in referidos_iniciales]
    registros = []

    for d in range(1, dias + 1):
        # Usuario: operar un día
        saldo_usuario_fin, ganancia_usuario_dia = operar_un_dia(saldo_usuario, porcentaje_beneficio_diario, num_cuantificaciones)

        # Referidos: operar un día y calcular comisión
        ganancia_referidos_dia_para_usuario = 0.0
        nuevos_referidos = []
        for r in referidos_sim:
            saldo_r_fin, ganancia_r_dia = operar_un_dia(r["saldo"], porcentaje_beneficio_diario, num_cuantificaciones)
            comision = COMISIONES.get(r["nivel"], 0.0) / 100.0
            ganancia_referidos_dia_para_usuario += ganancia_r_dia * comision
            nuevos_referidos.append({"nivel": r["nivel"], "saldo": saldo_r_fin})

        # Aplicar retiradas al final del día (usuario y referidos)
        if saldo_usuario_fin >= saldo_retiro and importe_retiro > 0:
            saldo_usuario_fin = max(0.0, saldo_usuario_fin - importe_retiro)

        for r in nuevos_referidos:
            if r["saldo"] >= saldo_retiro and importe_retiro > 0:
                r["saldo"] = max(0.0, r["saldo"] - importe_retiro)

        # Registrar
        registros.append({
            "Día": d,
            "Ganancia usuario (USDT)": round(ganancia_usuario_dia, 2),
            "Ganancia por referidos (USDT)": round(ganancia_referidos_dia_para_usuario, 2),
            "Ganancia total (USDT)": round(ganancia_usuario_dia + ganancia_referidos_dia_para_usuario, 2),
        })

        # Actualizar para el siguiente día
        saldo_usuario = saldo_usuario_fin
        referidos_sim = nuevos_referidos

    return registros, saldo_usuario, referidos_sim

if st.button("▶️ Calcular ganancias", type="primary"):
    # ----- Tabla diaria (90 días) -----
    registros_diarios, saldo_final_90, referidos_finales_90 = simular_periodo(90, saldo_inicial, st.session_state["referidos"])
    df_diario = pd.DataFrame(registros_diarios)
    st.subheader("Tabla diaria (90 días)")
    st.dataframe(df_diario, use_container_width=True)

    # Descargar CSV diario
    csv_diario = df_diario.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar resultados diarios CSV",
        data=csv_diario,
        file_name="simulacion_diaria.csv",
        mime="text/csv"
    )

    # ----- Tabla mensual (12 meses = 360 días), calculada día a día -----
    # Reiniciar al estado inicial para la simulación mensual
    saldo_mes = saldo_inicial
    referidos_mes = [{"nivel": r["nivel"], "saldo": float(r["saldo"])} for r in st.session_state["referidos"]]

    registros_mensuales = []
    for mes in range(1, 13):
        # Simula 30 días y acumula ganancias del mes
        registros_30, saldo_mes, referidos_mes = simular_periodo(30, saldo_mes, referidos_mes)
        # Sumar del bloque de 30 días
        ganancia_usuario_mes = sum(r["Ganancia usuario (USDT)"] for r in registros_30)
        ganancia_refs_mes = sum(r["Ganancia por referidos (USDT)"] for r in registros_30)

        registros_mensuales.append({
            "Mes": mes,
            "Ganancia usuario (USDT)": round(ganancia_usuario_mes, 2),
            "Ganancia por referidos (USDT)": round(ganancia_refs_mes, 2),
            "Ganancia total (USDT)": round(ganancia_usuario_mes + ganancia_refs_mes, 2),
        })

    df_mensual = pd.DataFrame(registros_mensuales)
    st.subheader("Tabla mensual (12 meses, cada mes = 30 días simulados)")
    st.dataframe(df_mensual, use_container_width=True)

    # Descargar CSV mensual
    csv_mensual = df_mensual.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar resultados mensuales CSV",
        data=csv_mensual,
        file_name="simulacion_mensual.csv",
        mime="text/csv"
    )

else:
    st.info("Configura los parámetros y pulsa **Calcular ganancias**.")
# simulador_ganancias_streamlit.py (Streamlit)
# Ejecuta: streamlit run simulador_ganancias_streamlit.py

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador de Ganancias USDT", layout="wide")
st.title("💰 Simulador de Ganancias con Referidos y Retiradas (USDT)")

# -------------------------------
# Helpers
# -------------------------------
def parse_float(txt: str, default: float = 0.0) -> float:
    try:
        txt = (txt or "").strip().replace(" ", "").replace(",", ".")
        if txt == "":
            return default
        return float(txt)
    except Exception:
        return default

def parse_int(txt: str, default: int = 1) -> int:
    try:
        txt = (txt or "").strip().replace(" ", "").replace(",", ".")
        if txt == "":
            return default
        # Acepta números escritos como "4", "4.0", etc.
        return int(float(txt))
    except Exception:
        return default

def operar_un_dia(saldo_inicial: float, pct_diario: float, cuantificaciones: int):
    """
    Aplica el beneficio diario en 'cuantificaciones' partes.
    Devuelve (saldo_final_del_dia, ganancia_dia).
    """
    saldo = saldo_inicial
    ganancia = 0.0
    if cuantificaciones < 1:
        cuantificaciones = 1
    for _ in range(cuantificaciones):
        g = saldo * (pct_diario / 100.0) / cuantificaciones
        saldo += g
        ganancia += g
    return saldo, ganancia

# -------------------------------
# Parámetros de operación
# -------------------------------
st.subheader("Parámetros de operación")

# Nº de cuantificaciones (texto para permitir libre edición)
if "num_cuantificaciones_txt" not in st.session_state:
    st.session_state["num_cuantificaciones_txt"] = "4"
num_cuantificaciones_txt = st.text_input(
    "Número de cuantificaciones diarias",
    value=st.session_state["num_cuantificaciones_txt"],
    help="Se reparte el beneficio diario en ese número de operaciones."
)
st.session_state["num_cuantificaciones_txt"] = num_cuantificaciones_txt
num_cuantificaciones = parse_int(num_cuantificaciones_txt, default=4)
if num_cuantificaciones < 1:
    num_cuantificaciones = 1

# Beneficio propio diario % (texto para permitir coma/decimal)
if "beneficio_diario_txt" not in st.session_state:
    st.session_state["beneficio_diario_txt"] = "1.0"
beneficio_diario_txt = st.text_input(
    "Beneficio propio diario (%)",
    value=st.session_state["beneficio_diario_txt"],
    help="Porcentaje diario. Ej.: 1,7 significa 1.7% al día."
)
st.session_state["beneficio_diario_txt"] = beneficio_diario_txt
porcentaje_beneficio_diario = parse_float(beneficio_diario_txt, default=1.0)
if porcentaje_beneficio_diario < 0:
    porcentaje_beneficio_diario = 0.0

# Saldo inicial (texto para permitir coma/decimal). Debe iniciar en 0.
if "saldo_inicial_txt" not in st.session_state:
    st.session_state["saldo_inicial_txt"] = "0"
saldo_inicial_txt = st.text_input(
    "Saldo inicial del usuario (USDT)",
    value=st.session_state["saldo_inicial_txt"]
)
st.session_state["saldo_inicial_txt"] = saldo_inicial_txt
saldo_inicial = parse_float(saldo_inicial_txt, default=0.0)
if saldo_inicial < 0:
    saldo_inicial = 0.0

# -------------------------------
# Configuración de retiradas
# -------------------------------
st.subheader("Configuración de retiradas periódicas")

if "saldo_retiro_txt" not in st.session_state:
    st.session_state["saldo_retiro_txt"] = "500"
saldo_retiro_txt = st.text_input(
    "Saldo a partir del cual se realiza la retirada (USDT)",
    value=st.session_state["saldo_retiro_txt"],
    help="Cuando el saldo al final del día alcance o supere este valor, se retira el importe configurado."
)
st.session_state["saldo_retiro_txt"] = saldo_retiro_txt
saldo_retiro = parse_float(saldo_retiro_txt, default=500.0)

if "importe_retiro_txt" not in st.session_state:
    st.session_state["importe_retiro_txt"] = "100"
importe_retiro_txt = st.text_input(
    "Importe a retirar cuando se alcanza el saldo de retirada (USDT)",
    value=st.session_state["importe_retiro_txt"]
)
st.session_state["importe_retiro_txt"] = importe_retiro_txt
importe_retiro = parse_float(importe_retiro_txt, default=100.0)
if importe_retiro < 0:
    importe_retiro = 0.0

# -------------------------------
# Gestión de referidos
# -------------------------------
st.subheader("Gestión de referidos (saldo y nivel)")

if "referidos" not in st.session_state:
    st.session_state["referidos"] = []  # cada elem: {"nivel": "A|B|C", "saldo": float}

with st.expander("➕ Añadir referido"):
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        nivel_nuevo = st.selectbox("Nivel", ["A", "B", "C"], index=0, key="nivel_nuevo")
    with col2:
        saldo_nuevo_txt = st.text_input("Saldo del referido (USDT)", value="0", key="saldo_nuevo_txt")
    with col3:
        if st.button("Añadir", use_container_width=True):
            saldo_nuevo = parse_float(saldo_nuevo_txt, default=0.0)
            if saldo_nuevo < 0:
                saldo_nuevo = 0.0
            st.session_state["referidos"].append({"nivel": nivel_nuevo, "saldo": saldo_nuevo})
            st.success("Referido añadido")

# Mostrar y permitir eliminar
if st.session_state["referidos"]:
    df_ref = pd.DataFrame([
        {"Nivel": r["nivel"], "Saldo (USDT)": round(float(r["saldo"]), 6)}
        for r in st.session_state["referidos"]
    ])
    st.dataframe(df_ref, use_container_width=True)
    idx_del = st.number_input("Eliminar referido (índice, empezando en 0)", min_value=0, max_value=len(st.session_state["referidos"])-1, value=0, step=1)
    if st.button("Eliminar referido seleccionado"):
        st.session_state["referidos"].pop(int(idx_del))
        st.success("Referido eliminado")

# Comisiones por nivel (en %)
COMISIONES = {"A": 19.0, "B": 7.0, "C": 3.0}

# -------------------------------
# Simulación
# -------------------------------
st.subheader("Simulación de Beneficios")

def simular_periodo(dias: int, saldo_usuario_inicial: float, referidos_iniciales: list):
    """
    Simula 'dias' días, aplicando:
      - beneficio diario dividido en N cuantificaciones
      - retirada al final del día si el saldo >= saldo_retiro
      - referidos con misma lógica (su saldo crece y también se someten a retiradas)
    Retorna:
      - registros_diarios: lista de dicts con resultados del día
      - saldo_usuario_final, referidos_finales
    """
    saldo_usuario = float(saldo_usuario_inicial)
    referidos_sim = [{"nivel": r["nivel"], "saldo": float(r["saldo"])} for r in referidos_iniciales]
    registros = []

    for d in range(1, dias + 1):
        # Usuario: operar un día
        saldo_usuario_fin, ganancia_usuario_dia = operar_un_dia(saldo_usuario, porcentaje_beneficio_diario, num_cuantificaciones)

        # Referidos: operar un día y calcular comisión
        ganancia_referidos_dia_para_usuario = 0.0
        nuevos_referidos = []
        for r in referidos_sim:
            saldo_r_fin, ganancia_r_dia = operar_un_dia(r["saldo"], porcentaje_beneficio_diario, num_cuantificaciones)
            comision = COMISIONES.get(r["nivel"], 0.0) / 100.0
            ganancia_referidos_dia_para_usuario += ganancia_r_dia * comision
            nuevos_referidos.append({"nivel": r["nivel"], "saldo": saldo_r_fin})

        # Aplicar retiradas al final del día (usuario y referidos)
        if saldo_usuario_fin >= saldo_retiro and importe_retiro > 0:
            saldo_usuario_fin = max(0.0, saldo_usuario_fin - importe_retiro)

        for r in nuevos_referidos:
            if r["saldo"] >= saldo_retiro and importe_retiro > 0:
                r["saldo"] = max(0.0, r["saldo"] - importe_retiro)

        # Registrar
        registros.append({
            "Día": d,
            "Ganancia usuario (USDT)": round(ganancia_usuario_dia, 2),
            "Ganancia por referidos (USDT)": round(ganancia_referidos_dia_para_usuario, 2),
            "Ganancia total (USDT)": round(ganancia_usuario_dia + ganancia_referidos_dia_para_usuario, 2),
        })

        # Actualizar para el siguiente día
        saldo_usuario = saldo_usuario_fin
        referidos_sim = nuevos_referidos

    return registros, saldo_usuario, referidos_sim

if st.button("▶️ Calcular ganancias", type="primary"):
    # ----- Tabla diaria (90 días) -----
    registros_diarios, saldo_final_90, referidos_finales_90 = simular_periodo(90, saldo_inicial, st.session_state["referidos"])
    df_diario = pd.DataFrame(registros_diarios)
    st.subheader("Tabla diaria (90 días)")
    st.dataframe(df_diario, use_container_width=True)

    # Descargar CSV diario
    csv_diario = df_diario.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar resultados diarios CSV",
        data=csv_diario,
        file_name="simulacion_diaria.csv",
        mime="text/csv"
    )

    # ----- Tabla mensual (12 meses = 360 días), calculada día a día -----
    # Reiniciar al estado inicial para la simulación mensual
    saldo_mes = saldo_inicial
    referidos_mes = [{"nivel": r["nivel"], "saldo": float(r["saldo"])} for r in st.session_state["referidos"]]

    registros_mensuales = []
    for mes in range(1, 13):
        # Simula 30 días y acumula ganancias del mes
        registros_30, saldo_mes, referidos_mes = simular_periodo(30, saldo_mes, referidos_mes)
        # Sumar del bloque de 30 días
        ganancia_usuario_mes = sum(r["Ganancia usuario (USDT)"] for r in registros_30)
        ganancia_refs_mes = sum(r["Ganancia por referidos (USDT)"] for r in registros_30)

        registros_mensuales.append({
            "Mes": mes,
            "Ganancia usuario (USDT)": round(ganancia_usuario_mes, 2),
            "Ganancia por referidos (USDT)": round(ganancia_refs_mes, 2),
            "Ganancia total (USDT)": round(ganancia_usuario_mes + ganancia_refs_mes, 2),
        })

    df_mensual = pd.DataFrame(registros_mensuales)
    st.subheader("Tabla mensual (12 meses, cada mes = 30 días simulados)")
    st.dataframe(df_mensual, use_container_width=True)

    # Descargar CSV mensual
    csv_mensual = df_mensual.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar resultados mensuales CSV",
        data=csv_mensual,
        file_name="simulacion_mensual.csv",
        mime="text/csv"
    )

else:
    st.info("Configura los parámetros y pulsa **Calcular ganancias**.")
