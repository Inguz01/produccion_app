import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# Columnas reales del CSV
COLUMNAS = [
    "Referencia", "Versión", "Fecha", "Cliente", "Fórmula", "Color", "Laminado", "Imagen",
    "Dureza", "Temperatura", "Presión", "Peso", "Cavidades", "Tacado", "Vulcanizado",
    "TiempoTotal", "PromedioHora", "TiempoCorteUnidad", "CorteHora", "CorteDiario",
    "Jornada", "Observaciones"
]

def cargar_fichas(fichas_path):
    """Carga el CSV y asegura que tenga todas las columnas."""
    if not os.path.exists(fichas_path):
        return pd.DataFrame(columns=COLUMNAS)
    df = pd.read_csv(fichas_path)
    for col in COLUMNAS:
        if col not in df.columns:
            df[col] = ""
    return df

def registrar_ficha(clientes_csv_path, fichas_path, img_dir, data_existente=None, es_nueva_version=False):
    st.header("📑 Registro de Ficha Técnica")

    fichas_df = cargar_fichas(fichas_path)
    clientes_df = pd.read_csv(clientes_csv_path) if os.path.exists(clientes_csv_path) else pd.DataFrame(columns=["Cliente"])

    if clientes_df.empty:
        st.warning("⚠️ Debe registrar clientes antes de crear fichas técnicas.")
        return

    if data_existente is None:
        data_existente = {c: "" for c in COLUMNAS}

    with st.form("form_ficha"):
        referencia = st.text_input("Referencia", value=data_existente.get("Referencia", "")).strip()
        cliente = st.selectbox("Cliente", clientes_df["Cliente"].tolist(),
                                index=clientes_df.index[clientes_df["Cliente"] == data_existente.get("Cliente", "")][0]
                                if data_existente.get("Cliente") in clientes_df["Cliente"].tolist() else 0)
        formula = st.text_input("Fórmula", value=data_existente.get("Fórmula", "")).strip()
        color = st.text_input("Color", value=data_existente.get("Color", "")).strip()
        laminado = st.number_input("Laminado (mm)", min_value=1.0, step=0.1,
                                    value=float(data_existente.get("Laminado", 1) or 1.0))
        dureza = st.number_input("Dureza", min_value=1.0, step=0.1,
                                  value=float(data_existente.get("Dureza", 1) or 1.0))
        temperatura = st.number_input("Temperatura (°C)", min_value=1.0, step=0.1,
                                      value=float(data_existente.get("Temperatura", 1) or 1.0))
        presion = st.number_input("Presión (psi)", min_value=1.0, step=0.1,
                                   value=float(data_existente.get("Presión", 1) or 1.0))
        peso = st.number_input("Peso del producto (g)", min_value=1.0, step=0.1,
                                value=float(data_existente.get("Peso", 1) or 1.0))
        cavidades = st.number_input("Cavidades", min_value=1, step=1,
                                     value=int(data_existente.get("Cavidades", 1) or 1))
        tacado = st.number_input("Tiempo Tacado (s)", min_value=1, step=1,
                                  value=int(data_existente.get("Tacado", 1) or 1))
        vulcanizado = st.number_input("Tiempo Vulcanizado (s)", min_value=1, step=1,
                                       value=int(data_existente.get("Vulcanizado", 1) or 1))
        tiempo_total = tacado + vulcanizado
        promedio_hora = st.number_input("Producción Promedio Hora (uds)", min_value=1, step=1,
                                         value=int(data_existente.get("PromedioHora", 1) or 1))
        tiempo_corte = st.number_input("Tiempo Corte Unidad (s)", min_value=1, step=1,
                                        value=int(data_existente.get("TiempoCorteUnidad", 1) or 1))
        corte_hora = st.number_input("Producción Corte Hora (uds)", min_value=1, step=1,
                                      value=int(data_existente.get("CorteHora", 1) or 1))
        corte_diario = st.number_input("Producción Corte Diario (uds)", min_value=1, step=1,
                                        value=int(data_existente.get("CorteDiario", 1) or 1))
        jornada = st.selectbox("Jornada", ["Mañana", "Tarde", "Noche"],
                                index=["Mañana", "Tarde", "Noche"].index(data_existente.get("Jornada", "Mañana"))
                                if data_existente.get("Jornada") in ["Mañana", "Tarde", "Noche"] else 0)
        observaciones = st.text_area("Observaciones", value=data_existente.get("Observaciones", ""))
        imagen = st.file_uploader("Imagen de la referencia", type=["jpg", "jpeg", "png"])

        guardar = st.form_submit_button("💾 Guardar Ficha")

        if guardar:
            if not all([referencia, cliente, formula, color]):
                st.error("⚠️ Todos los campos de texto son obligatorios.")
                return

            for val, name in [(laminado, "Laminado"), (dureza, "Dureza"), (temperatura, "Temperatura"),
                              (presion, "Presión"), (peso, "Peso"), (cavidades, "Cavidades"),
                              (tacado, "Tacado"), (vulcanizado, "Vulcanizado"), (promedio_hora, "PromedioHora"),
                              (tiempo_corte, "Tiempo Corte"), (corte_hora, "Corte Hora"), (corte_diario, "Corte Diario")]:
                if val <= 0:
                    st.error(f"⚠️ El valor de {name} no puede ser cero.")
                    return

            if es_nueva_version:
                cambios = any(str(data_existente.get(campo, "")) != str(locals().get(campo.lower(), "")) for campo in
                              ["Fórmula", "Color", "Laminado", "Dureza", "Temperatura", "Presión", "Peso",
                               "Cavidades", "Tacado", "Vulcanizado", "PromedioHora", "TiempoCorteUnidad",
                               "CorteHora", "CorteDiario", "Jornada", "Observaciones"])
                if not cambios:
                    st.error("⚠️ Debe modificar al menos un dato para crear una nueva versión.")
                    return

            versiones_existentes = fichas_df[(fichas_df["Cliente"].str.lower() == cliente.lower()) &
                                             (fichas_df["Referencia"].str.lower() == referencia.lower())]
            version = 1 if versiones_existentes.empty else versiones_existentes["Versión"].max() + 1
            fecha = datetime.today().strftime("%Y-%m-%d")

            # Guardar imagen (solo nombre en CSV)
            imagen_nombre = data_existente.get("Imagen", "")
            if imagen:
                os.makedirs(img_dir, exist_ok=True)
                imagen_nombre = f"imagen_{imagen.name}"
                ruta_completa = os.path.join(img_dir, imagen_nombre)
                with open(ruta_completa, "wb") as f:
                    f.write(imagen.getbuffer())

            nueva_ficha = pd.DataFrame([{
                "Referencia": referencia, "Versión": version, "Fecha": fecha,
                "Cliente": cliente, "Fórmula": formula, "Color": color, "Laminado": laminado,
                "Imagen": imagen_nombre, "Dureza": dureza, "Temperatura": temperatura, "Presión": presion,
                "Peso": peso, "Cavidades": cavidades, "Tacado": tacado, "Vulcanizado": vulcanizado,
                "TiempoTotal": tiempo_total, "PromedioHora": promedio_hora,
                "TiempoCorteUnidad": tiempo_corte, "CorteHora": corte_hora, "CorteDiario": corte_diario,
                "Jornada": jornada, "Observaciones": observaciones
            }])

            fichas_df = pd.concat([fichas_df, nueva_ficha], ignore_index=True)
            fichas_df.to_csv(fichas_path, index=False)
            st.success(f"✅ Ficha técnica guardada (Versión {version}).")
            time.sleep(2)
            st.rerun()

def visualizar_ficha(fichas_path, img_dir):
    st.header("🔍 Visualización de Fichas Técnicas")

    fichas_df = cargar_fichas(fichas_path)
    if fichas_df.empty:
        st.warning("No hay fichas técnicas registradas.")
        return

    clientes = fichas_df["Cliente"].dropna().unique().tolist()
    cliente = st.selectbox("Seleccionar Cliente", clientes)
    referencias = fichas_df[fichas_df["Cliente"] == cliente]["Referencia"].dropna().unique().tolist()
    referencia = st.selectbox("Seleccionar Referencia", referencias)

    versiones = fichas_df[(fichas_df["Cliente"] == cliente) & (fichas_df["Referencia"] == referencia)].sort_values("Versión", ascending=False)
    ultima = versiones.iloc[0]

    st.subheader(f"Ficha Técnica - {referencia} (Versión {ultima.get('Versión', 'N/A')})")
    st.write(f"**Fecha:** {ultima.get('Fecha', 'N/A')} | **Cliente:** {cliente}")
    st.write(f"**Fórmula:** {ultima.get('Fórmula', 'N/A')} | **Color:** {ultima.get('Color', 'N/A')} | **Laminado:** {ultima.get('Laminado', 'N/A')} mm")
    st.write(f"**Dureza:** {ultima.get('Dureza', 'N/A')} | **Temperatura:** {ultima.get('Temperatura', 'N/A')} °C | **Presión:** {ultima.get('Presión', 'N/A')} psi")
    st.write(f"**Peso:** {ultima.get('Peso', 'N/A')} g | **Cavidades:** {ultima.get('Cavidades', 'N/A')}")
    st.write(f"**Tacado:** {ultima.get('Tacado', 'N/A')}s | **Vulcanizado:** {ultima.get('Vulcanizado', 'N/A')}s | **Tiempo Total:** {ultima.get('TiempoTotal', 'N/A')}s")
    st.write(f"**Promedio Hora:** {ultima.get('PromedioHora', 'N/A')} uds/h")
    st.write(f"**Tiempo Corte Unidad:** {ultima.get('TiempoCorteUnidad', 'N/A')}s | **Corte Hora:** {ultima.get('CorteHora', 'N/A')} uds | **Corte Diario:** {ultima.get('CorteDiario', 'N/A')} uds")
    st.write(f"**Jornada:** {ultima.get('Jornada', 'N/A')}")
    st.write(f"**Observaciones:** {ultima.get('Observaciones', 'N/A')}")

    # Mostrar imagen desde img_dir
    imagen_nombre = ultima.get("Imagen")
    if isinstance(imagen_nombre, str) and imagen_nombre.strip() != "":
        imagen_ruta = os.path.join(img_dir, imagen_nombre)
        if os.path.exists(imagen_ruta):
            st.image(imagen_ruta, caption="Imagen de la referencia", width=300)
        else:
            st.warning("📷 La imagen no se encontró en la carpeta de imágenes.")
    else:
        st.warning("📷 No hay imagen disponible para esta ficha.")

    if st.session_state.rol == "Administrador":
        with st.expander("📜 Ver historial de versiones"):
            st.dataframe(versiones[["Versión", "Fecha", "Fórmula", "Color", "Laminado", "Dureza"]])

        if st.button("➕ Generar nueva versión"):
            registrar_ficha(st.session_state.clientes_csv_path, fichas_path, img_dir, ultima.to_dict(), es_nueva_version=True)

