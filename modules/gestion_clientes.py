import streamlit as st
import pandas as pd
import time
import os

def gestionar_clientes(clientes_csv_path):
    st.header("📋 Gestión de Clientes")
    columnas = ["Cliente", "NIT", "Dirección", "Teléfono", "Correo", "Contacto1", "Correo1", "Contacto2", "Correo2"]

    # Cargar clientes
    if not hasattr(st.session_state, "pagina_clientes"):
        st.session_state.pagina_clientes = 1
    if not hasattr(st.session_state, "mostrar_form"):
        st.session_state.mostrar_form = False
    if not hasattr(st.session_state, "editar_nit"):
        st.session_state.editar_nit = None

    if st.session_state.get("reset_form"):
        st.session_state.mostrar_form = False
        st.session_state.editar_nit = None
        st.session_state.reset_form = False

    if clientes_csv_path.endswith(".csv") and st.session_state.get("csv_initialized") is None:
        if not os.path.exists(clientes_csv_path):
            pd.DataFrame(columns=columnas).to_csv(clientes_csv_path, index=False)
        st.session_state.csv_initialized = True

    clientes_df = pd.read_csv(clientes_csv_path) if len(open(clientes_csv_path).read().strip()) else pd.DataFrame(columns=columnas)

    # Filtros y paginación
    st.markdown("### 🔍 Buscar Cliente")
    filtro = st.text_input("Buscar por nombre o NIT")
    st.markdown("### 📄 Clientes por página")
    clientes_por_pagina = st.selectbox("Clientes por página", [10, 20, 50], index=0)

    if filtro:
        filtrado_df = clientes_df[
            clientes_df.apply(lambda x: filtro.lower() in str(x['Cliente']).lower() or filtro in str(x['NIT']), axis=1)
        ]
    else:
        filtrado_df = clientes_df

    total_paginas = max(1, (len(filtrado_df) - 1) // clientes_por_pagina + 1)
    pagina_actual = st.session_state.pagina_clientes

    if pagina_actual > total_paginas:
        pagina_actual = total_paginas

    start = (pagina_actual - 1) * clientes_por_pagina
    end = start + clientes_por_pagina
    pagina_df = filtrado_df.iloc[start:end]

    # Encabezados
    cols_head = st.columns([2, 2, 2, 2, 2, 2, 0.5, 0.5])
    headers = ["Cliente", "NIT", "Dirección", "Teléfono", "Contacto1", "Correo1", "", ""]
    for col, h in zip(cols_head, headers):
        col.markdown(f"**{h}**")

    # Listado
    if not pagina_df.empty:
        for i, row in pagina_df.iterrows():
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 2, 2, 2, 2, 2, 0.5, 0.5])
            col1.write(row.Cliente)
            col2.write(row.NIT)
            col3.write(row.Dirección)
            col4.write(row.Teléfono)
            col5.write(row.Contacto1)
            col6.write(row.Correo1)
            if col7.button("✏️", key=f"editar_{row.NIT}"):
                st.session_state.editar_nit = row.NIT
                st.session_state.mostrar_form = True
                st.rerun()
            if col8.button("🗑️", key=f"eliminar_{row.NIT}"):
                clientes_df = clientes_df[clientes_df["NIT"] != row.NIT]
                clientes_df.to_csv(clientes_csv_path, index=False)
                st.success("✅ Cliente eliminado")
                time.sleep(1)
                st.rerun()
    else:
        st.info("No hay clientes registrados aún.")

    # Paginación
    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    if col_pag1.button("⬅️ Anterior") and pagina_actual > 1:
        st.session_state.pagina_clientes = pagina_actual - 1
        st.rerun()
    col_pag2.write(f"Página {pagina_actual} de {total_paginas}")
    if col_pag3.button("Siguiente ➡️") and pagina_actual < total_paginas:
        st.session_state.pagina_clientes = pagina_actual + 1
        st.rerun()

    # Botón Registrar
    st.markdown("---")
    if st.button("➕ Registrar Cliente"):
        st.session_state.mostrar_form = True
        st.session_state.editar_nit = None

    # Formulario
    if st.session_state.mostrar_form:
        st.subheader("🧾 Formulario Cliente")
        if st.session_state.editar_nit:
            cliente = clientes_df[clientes_df["NIT"] == st.session_state.editar_nit].iloc[0]
        else:
            cliente = pd.Series({c: "" for c in columnas})

        with st.form("form_cliente"):
            nombre = st.text_input("Nombre del cliente", cliente.Cliente)
            nit = st.text_input("NIT", str(cliente.NIT))
            direccion = st.text_input("Dirección", cliente.Dirección)
            telefono = st.text_input("Teléfono", str(cliente.Teléfono))
            contacto1 = st.text_input("Contacto 1", cliente.Contacto1)
            correo1 = st.text_input("Correo contacto 1", cliente.Correo1)
            contacto2 = st.text_input("Contacto 2", cliente.Contacto2)
            correo2 = st.text_input("Correo contacto 2", cliente.Correo2)

            guardar = st.form_submit_button("💾 Guardar")
            if guardar:
                if not all([nombre, nit, direccion, telefono, contacto1, correo1]):
                    st.error("⚠️ Todos los campos excepto Contacto 2 y Correo 2 son obligatorios.")
                elif not nit.isdigit() or len(nit) != 10:
                    st.error("⚠️ El NIT debe tener 10 dígitos.")
                elif not telefono.isdigit() or len(telefono) != 10:
                    st.error("⚠️ El teléfono debe tener 10 dígitos.")
                elif "@" not in correo1:
                    st.error("⚠️ Correo 1 no válido.")
                elif correo2 and "@" not in correo2:
                    st.error("⚠️ Correo 2 no válido.")
                elif nit in clientes_df["NIT"].astype(str).tolist() and nit != str(st.session_state.editar_nit):
                    st.error("⚠️ Ya existe otro cliente con ese NIT.")
                else:
                    nuevo = pd.DataFrame([{
                        "Cliente": nombre, "NIT": nit, "Dirección": direccion, "Teléfono": telefono,
                        "Correo": "", "Contacto1": contacto1, "Correo1": correo1, "Contacto2": contacto2, "Correo2": correo2
                    }])
                    if st.session_state.editar_nit:
                        clientes_df.loc[clientes_df["NIT"] == st.session_state.editar_nit] = nuevo.values
                        st.success("✅ Cliente actualizado.")
                    else:
                        clientes_df = pd.concat([clientes_df, nuevo], ignore_index=True)
                        st.success("✅ Cliente registrado.")
                    clientes_df.to_csv(clientes_csv_path, index=False)
                    time.sleep(2)
                    st.session_state.reset_form = True
                    st.rerun()
