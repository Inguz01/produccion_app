import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# Columnas esperadas
OP_COLUMNS = ["ID_OP", "Cliente", "Fecha_Creacion", "Estado"]
DETALLE_OP_COLUMNS = ["ID_OP", "Referencia", "Cantidad_Producir", "OC_Origen", "Cantidad_OC", "Fecha_Entrega", "clave"]

def registrar_op(ordenes_path, detalles_path, op_path, detalle_op_path):
    st.header("🏭 Registrar Orden de Producción")

    # Crear archivos si no existen
    if not os.path.exists(op_path):
        pd.DataFrame(columns=OP_COLUMNS).to_csv(op_path, index=False)
    if not os.path.exists(detalle_op_path):
        pd.DataFrame(columns=DETALLE_OP_COLUMNS).to_csv(detalle_op_path, index=False)

    # Validar existencia de órdenes de compra
    if not os.path.exists(ordenes_path) or os.stat(ordenes_path).st_size == 0:
        st.warning("⚠️ No hay órdenes de compra registradas.")
        return

    ordenes_df = pd.read_csv(ordenes_path)
    detalles_df = pd.read_csv(detalles_path) if os.path.exists(detalles_path) else pd.DataFrame()
    op_df = pd.read_csv(op_path)
    detalle_op_df = pd.read_csv(detalle_op_path)

    if detalles_df.empty:
        st.warning("⚠️ No hay referencias en detalle de OC.")
        return

    # Seleccionar cliente
    clientes = ordenes_df["Cliente"].unique().tolist()
    cliente = st.selectbox("Seleccionar Cliente", clientes)

    oc_cliente = ordenes_df[ordenes_df["Cliente"] == cliente]
    if oc_cliente.empty:
        st.info("Este cliente no tiene órdenes.")
        return

    # Calcular pendientes: Cantidad - Producido
    detalles_cliente = detalles_df[detalles_df["ID_Orden"].isin(oc_cliente["ID_Orden"])]
    detalles_cliente["Pendiente"] = detalles_cliente["Cantidad"] - detalles_cliente["Producido"]

    # Filtrar solo pendientes > 0
    pendientes = detalles_cliente[detalles_cliente["Pendiente"] > 0]

    if pendientes.empty:
        st.info("✅ Todas las referencias para este cliente están completadas.")
        return

    # Evitar referencias ya usadas en OP (clave)
    claves_usadas = set(detalle_op_df["clave"].tolist())
    pendientes["clave"] = pendientes.apply(lambda r: f"{r['ID_Orden']}_{r['Referencia']}", axis=1)
    pendientes = pendientes[~pendientes["clave"].isin(claves_usadas)]

    if pendientes.empty:
        st.info("✅ No hay referencias pendientes para generar OP.")
        return

    st.subheader("📦 Referencias pendientes para generar OP")
    st.dataframe(pendientes[["ID_Orden", "Referencia", "Pendiente", "Fecha_Entrega"]])

    st.markdown("### Selección de referencias para producir")
    seleccionadas = []
    for idx, row in pendientes.iterrows():
        col1, col2 = st.columns([3, 2])
        with col1:
            sel = st.checkbox(f"{row['Referencia']} (OC {row['ID_Orden']})", key=f"chk_{idx}")
        if sel:
            with col2:
                cant = st.number_input(
                    f"Cantidad ({row['Referencia']})",
                    min_value=1,
                    max_value=int(row["Pendiente"]),
                    value=int(row["Pendiente"]),
                    key=f"cant_{idx}"
                )
            seleccionadas.append({
                "ID_Orden": row["ID_Orden"],
                "Referencia": row["Referencia"],
                "Cantidad_Producir": cant,
                "Cantidad_OC": row["Cantidad"],
                "Fecha_Entrega": row["Fecha_Entrega"],
                "clave": row["clave"]
            })

    if st.button("💾 Registrar OP"):
        if not seleccionadas:
            st.error("⚠️ Debe seleccionar al menos una referencia.")
            return

        # Crear ID_OP
        nuevo_id_op = op_df["ID_OP"].max() + 1 if not op_df.empty else 1

        # Guardar en OP
        nueva_op = pd.DataFrame([{
            "ID_OP": nuevo_id_op,
            "Cliente": cliente,
            "Fecha_Creacion": datetime.today().strftime("%Y-%m-%d"),
            "Estado": "Pendiente"
        }])
        op_df = pd.concat([op_df, nueva_op], ignore_index=True)
        op_df.to_csv(op_path, index=False)

        # Guardar detalles OP
        nuevos_detalles = pd.DataFrame([{
            "ID_OP": nuevo_id_op,
            "Referencia": s["Referencia"],
            "Cantidad_Producir": s["Cantidad_Producir"],
            "OC_Origen": s["ID_Orden"],
            "Cantidad_OC": s["Cantidad_OC"],
            "Fecha_Entrega": s["Fecha_Entrega"],
            "clave": s["clave"]
        } for s in seleccionadas])
        detalle_op_df = pd.concat([detalle_op_df, nuevos_detalles], ignore_index=True)
        detalle_op_df.to_csv(detalle_op_path, index=False)

        st.success(f"✅ OP {nuevo_id_op} registrada con {len(seleccionadas)} referencias.")
        time.sleep(2)
        st.rerun()

def visualizar_op(op_path, detalle_op_path, produccion_real_path, ordenes_path):
    st.header("📋 Órdenes de Producción")

    if not os.path.exists(op_path) or os.stat(op_path).st_size == 0:
        st.warning("No hay órdenes de producción registradas.")
        return

    op_df = pd.read_csv(op_path)
    detalle_op_df = pd.read_csv(detalle_op_path) if os.path.exists(detalle_op_path) else pd.DataFrame()
    ordenes_df = pd.read_csv(ordenes_path) if os.path.exists(ordenes_path) else pd.DataFrame()

    if op_df.empty:
        st.info("No hay OP registradas.")
        return

    st.subheader("Lista de Órdenes de Producción")
    if detalle_op_df.empty:
        st.info("No hay detalles asociados a las OP.")
        return

    # Unir con OC para mostrar Numero_OC_Cliente
    merged = detalle_op_df.merge(op_df, on="ID_OP", how="left").merge(ordenes_df, left_on="OC_Origen", right_on="ID_Orden", how="left")

    st.dataframe(merged[[
        "ID_OP", "Cliente_x", "OC_Origen", "Numero_OC_Cliente", "Referencia",
        "Cantidad_Producir", "Cantidad_OC", "Fecha_Entrega"
    ]].rename(columns={"Cliente_x": "Cliente"}))

