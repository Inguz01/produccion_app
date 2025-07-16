import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# Columnas esperadas
ORDENES_COLUMNS = ["ID_Orden", "Cliente", "Fecha_Recepcion", "Estado", "Numero_OC_Cliente"]
DETALLES_COLUMNS = ["ID_Orden", "Referencia", "Cantidad", "Fecha_Entrega", "Precio_Unitario", "Producido"]

def registrar_oc(clientes_path, fichas_path, ordenes_path, detalles_path):
    st.header("📝 Registro de Órdenes de Compra")

    # Crear archivos si no existen
    if not os.path.exists(ordenes_path):
        pd.DataFrame(columns=ORDENES_COLUMNS).to_csv(ordenes_path, index=False)
    if not os.path.exists(detalles_path):
        pd.DataFrame(columns=DETALLES_COLUMNS).to_csv(detalles_path, index=False)

    clientes_df = pd.read_csv(clientes_path) if os.path.exists(clientes_path) else pd.DataFrame(columns=["Cliente"])
    fichas_df = pd.read_csv(fichas_path) if os.path.exists(fichas_path) else pd.DataFrame(columns=["Cliente", "Referencia"])
    ordenes_df = pd.read_csv(ordenes_path)
    detalles_df = pd.read_csv(detalles_path)

    if clientes_df.empty:
        st.warning("⚠️ Debe registrar clientes antes de crear órdenes.")
        return
    if fichas_df.empty:
        st.warning("⚠️ Debe registrar fichas técnicas antes de crear órdenes.")
        return

    with st.form("form_oc"):
        cliente = st.selectbox("Cliente", clientes_df["Cliente"].tolist())
        numero_oc = st.text_input("Número de Orden de Compra (Cliente)").strip()

        # Filtrar referencias del cliente
        referencias_cliente = fichas_df[fichas_df["Cliente"] == cliente]["Referencia"].dropna().unique().tolist()
        if not referencias_cliente:
            st.warning("⚠️ Este cliente no tiene referencias registradas.")
            return

        st.write("### Seleccionar Referencias")
        referencias = []
        for idx, ref in enumerate(referencias_cliente):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
            with col1:
                sel = st.checkbox(f"{ref}", key=f"chk_{idx}_{ref}")
            if sel:
                with col2:
                    cant = st.number_input(f"Cantidad", min_value=1, value=1, key=f"cant_{idx}")
                with col3:
                    precio = st.number_input(f"Precio", min_value=0.01, value=1.00, step=0.01, key=f"precio_{idx}")
                with col4:
                    fecha_entrega = st.date_input(f"Entrega", key=f"fecha_{idx}")
                referencias.append({"Referencia": ref, "Cantidad": cant, "Precio": precio, "Fecha": fecha_entrega})

        guardar = st.form_submit_button("💾 Registrar OC")

        if guardar:
            # Validaciones
            if not numero_oc:
                st.error("⚠️ El número de orden es obligatorio.")
                return
            if not referencias:
                st.error("⚠️ Debe seleccionar al menos una referencia.")
                return

            # Validar duplicado (Cliente + Numero_OC_Cliente)
            duplicado = ordenes_df[
                (ordenes_df["Cliente"].str.lower() == cliente.lower()) &
                (ordenes_df["Numero_OC_Cliente"].str.lower() == numero_oc.lower())
            ]
            if not duplicado.empty:
                st.error("⚠️ Este número de orden ya existe para este cliente.")
                return

            for r in referencias:
                if r["Cantidad"] <= 0:
                    st.error(f"⚠️ La cantidad para {r['Referencia']} debe ser mayor a cero.")
                    return
                if r["Precio"] <= 0:
                    st.error(f"⚠️ El precio para {r['Referencia']} debe ser mayor a cero.")
                    return

            # Generar nuevo ID
            nuevo_id = ordenes_df["ID_Orden"].max() + 1 if not ordenes_df.empty else 1

            # Guardar en ordenes
            nueva_oc = pd.DataFrame([{
                "ID_Orden": nuevo_id,
                "Cliente": cliente,
                "Fecha_Recepcion": datetime.today().strftime("%Y-%m-%d"),
                "Estado": "Pendiente",
                "Numero_OC_Cliente": numero_oc
            }])
            ordenes_df = pd.concat([ordenes_df, nueva_oc], ignore_index=True)
            ordenes_df.to_csv(ordenes_path, index=False)

            # Guardar detalles (Producido = 0)
            nuevas_ref = pd.DataFrame([{
                "ID_Orden": nuevo_id,
                "Referencia": r["Referencia"],
                "Cantidad": r["Cantidad"],
                "Fecha_Entrega": r["Fecha"],
                "Precio_Unitario": r["Precio"],
                "Producido": 0
            } for r in referencias])
            detalles_df = pd.concat([detalles_df, nuevas_ref], ignore_index=True)
            detalles_df.to_csv(detalles_path, index=False)

            st.success(f"✅ Orden {numero_oc} registrada con {len(referencias)} referencias.")
            time.sleep(2)
            st.rerun()

def seguimiento_oc(ordenes_path, detalles_path):
    st.header("📋 Seguimiento de Órdenes de Compra")

    if not os.path.exists(ordenes_path) or os.stat(ordenes_path).st_size == 0:
        st.warning("No hay órdenes registradas.")
        return

    ordenes_df = pd.read_csv(ordenes_path)
    detalles_df = pd.read_csv(detalles_path) if os.path.exists(detalles_path) else pd.DataFrame(columns=DETALLES_COLUMNS)

    if ordenes_df.empty:
        st.warning("No hay órdenes registradas.")
        return

    clientes = ordenes_df["Cliente"].dropna().unique().tolist()
    cliente = st.selectbox("Seleccionar Cliente", clientes)

    oc_cliente = ordenes_df[ordenes_df["Cliente"] == cliente]
    if oc_cliente.empty:
        st.info("Este cliente no tiene órdenes.")
        return

    oc_seleccionada = st.selectbox("Seleccionar Número de OC", oc_cliente["Numero_OC_Cliente"].tolist())

    id_oc = oc_cliente[oc_cliente["Numero_OC_Cliente"] == oc_seleccionada]["ID_Orden"].values[0]
    detalles = detalles_df[detalles_df["ID_Orden"] == id_oc]

    if detalles.empty:
        st.info("Esta OC no tiene referencias.")
        return

    detalles["Pendiente"] = detalles["Cantidad"] - detalles["Producido"]
    st.write(f"### Detalles de la OC {oc_seleccionada}")
    st.dataframe(detalles[["Referencia", "Cantidad", "Producido", "Pendiente", "Precio_Unitario", "Fecha_Entrega"]])


