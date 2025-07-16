import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

def programar_produccion(op_path, detalle_op_path, programacion_path, maquinas_path):
    st.header("📅 Programación de Producción")

    # Crear archivos si no existen
    if not os.path.exists(programacion_path):
        pd.DataFrame(columns=["Fecha", "ID_OP", "Referencia", "Operario", "Maquina", "Hora_Inicio", "Hora_Fin"]).to_csv(programacion_path, index=False)
    if not os.path.exists(maquinas_path):
        pd.DataFrame(columns=["Maquina"]).to_csv(maquinas_path, index=False)

    if not os.path.exists(op_path) or os.stat(op_path).st_size == 0:
        st.warning("⚠️ No hay órdenes de producción registradas.")
        return

    op_df = pd.read_csv(op_path)
    detalle_op_df = pd.read_csv(detalle_op_path) if os.path.exists(detalle_op_path) else pd.DataFrame()
    programacion_df = pd.read_csv(programacion_path)
    maquinas_df = pd.read_csv(maquinas_path)

    if detalle_op_df.empty:
        st.warning("⚠️ No hay detalles de OP registrados.")
        return

    # Seleccionar OP
    id_op = st.selectbox("Seleccionar OP", op_df["ID_OP"].tolist())
    detalles = detalle_op_df[detalle_op_df["ID_OP"] == id_op]

    if detalles.empty:
        st.info("No hay referencias para esta OP.")
        return

    # Selección de fecha y máquina
    fecha = st.date_input("Fecha de programación", value=datetime.today())
    if maquinas_df.empty:
        st.warning("⚠️ No hay máquinas registradas. Agregue al menos una en el archivo maquinas.csv")
        return

    st.markdown("### Referencias de la OP")
    seleccionadas = []
    for idx, row in detalles.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
        with col1:
            st.write(row["Referencia"])
        with col2:
            maquina = st.selectbox(f"Máquina ({row['Referencia']})", maquinas_df["Maquina"].tolist(), key=f"maq_{idx}")
        with col3:
            operario = st.text_input(f"Operario ({row['Referencia']})", key=f"op_{idx}")
        with col4:
            hora_inicio = st.time_input(f"Inicio ({row['Referencia']})", key=f"ini_{idx}")
        with col5:
            hora_fin = st.time_input(f"Fin ({row['Referencia']})", key=f"fin_{idx}")

        seleccionadas.append({
            "Referencia": row["Referencia"],
            "Maquina": maquina,
            "Operario": operario,
            "Hora_Inicio": hora_inicio,
            "Hora_Fin": hora_fin
        })

    if st.button("💾 Guardar Programación"):
        errores = []
        for item in seleccionadas:
            if not item["Operario"]:
                errores.append(f"Falta operario para {item['Referencia']}")
            elif item["Hora_Inicio"] >= item["Hora_Fin"]:
                errores.append(f"Rango horario inválido en {item['Referencia']}")

        if errores:
            for e in errores:
                st.error(e)
            return

        # Validar solapamiento
        for item in seleccionadas:
            mismos_dia = programacion_df[(programacion_df["Fecha"] == str(fecha))]
            # Validar máquina
            conflicto_maquina = mismos_dia[(mismos_dia["Maquina"] == item["Maquina"]) &
                                           (mismos_dia["Hora_Inicio"] < str(item["Hora_Fin"])) &
                                           (mismos_dia["Hora_Fin"] > str(item["Hora_Inicio"]))]
            if not conflicto_maquina.empty:
                st.error(f"Conflicto: La máquina {item['Maquina']} ya está ocupada en este horario.")
                return
            # Validar operario
            conflicto_operario = mismos_dia[(mismos_dia["Operario"] == item["Operario"]) &
                                            (mismos_dia["Hora_Inicio"] < str(item["Hora_Fin"])) &
                                            (mismos_dia["Hora_Fin"] > str(item["Hora_Inicio"]))]
            if not conflicto_operario.empty:
                st.error(f"Conflicto: El operario {item['Operario']} ya está asignado en este horario.")
                return

        # Guardar programación
        nuevas_prog = pd.DataFrame([{
            "Fecha": str(fecha),
            "ID_OP": id_op,
            "Referencia": item["Referencia"],
            "Operario": item["Operario"],
            "Maquina": item["Maquina"],
            "Hora_Inicio": str(item["Hora_Inicio"]),
            "Hora_Fin": str(item["Hora_Fin"])
        } for item in seleccionadas])

        programacion_df = pd.concat([programacion_df, nuevas_prog], ignore_index=True)
        programacion_df.to_csv(programacion_path, index=False)
        st.success("✅ Programación guardada correctamente.")
        time.sleep(2)
        st.rerun()
