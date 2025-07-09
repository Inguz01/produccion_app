import streamlit as st
import pandas as pd
import os
import re
import time
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from datetime import time as dtime
from datetime import datetime
import streamlit.components.v1 as components
from datetime import date

#st.set_page_config(page_title="Rubber Soft", layout="wide")


# Crear carpeta de datos si no existe
if not os.path.exists("datos"):
    os.makedirs("datos")

# Archivo de producción real
produccion_path = "datos/produccion_real.csv"
if not os.path.exists(produccion_path):
    pd.DataFrame(columns=["ID_OP", "Referencia", "Cantidad_Producida", "Fecha_Registro", "OC_Origen"]).to_csv(produccion_path, index=False)

# Cargar siempre tema oscuro
if os.path.exists("datos/style_oscuro.css"):
    with open("datos/style_oscuro.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Cargar estilos visuales corporativos
if os.path.exists("datos/style.css"):
    with open("datos/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inicializar sesión
if "logueado" not in st.session_state:
    st.session_state["logueado"] = False
    st.session_state["usuario"] = ""
    st.session_state["rol"] = ""

if "tema" not in st.session_state:
    st.session_state["tema"] = "claro"  # Valor por defecto 

# Función de login
def login():
    st.markdown("<h1 style='text-align: center;'>🛡️ Inicio de Sesión</h1>", unsafe_allow_html=True)
    if os.path.exists("datos/logo_empresa.png"):
        st.image("datos/logo_empresa.png", width=150)

    with st.form("login_form"):
        usuario = st.text_input("👤 Usuario")
        clave = st.text_input("🔒 Contraseña", type="password")
        submit = st.form_submit_button("Iniciar sesión")

        if submit:
            if os.path.exists("datos/usuarios.csv"):
                df_usuarios = pd.read_csv("datos/usuarios.csv")
                usuario = usuario.strip()
                clave = clave.strip()
                user_row = df_usuarios[
                    (df_usuarios["usuario"].str.strip() == usuario) &
                    (df_usuarios["clave"].astype(str).str.strip() == clave)
                ]

                if not user_row.empty:
                    st.session_state["logueado"] = True
                    st.session_state["usuario"] = usuario
                    st.session_state["rol"] = user_row.iloc[0]["rol"]
                    st.rerun()
                else:
                    st.error("❌ Credenciales inválidas")
            else:
                st.error("Archivo usuarios.csv no encontrado.")

# Control de sesión
if not st.session_state["logueado"]:
    login()
else:
    # Mostrar barra lateral con botón de cerrar sesión
    st.sidebar.markdown(f"👤 Usuario: **{st.session_state['usuario']}**")
    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state["logueado"] = False
        st.session_state["usuario"] = ""
        st.session_state["rol"] = ""
        st.rerun()
    
    # Menú según el rol
    if st.session_state["rol"] == "Administrador":
        menu = st.sidebar.selectbox("Menú", 
        [
        "Registrar Cliente", 
        "Registrar Ficha Técnica", 
        "Visualizar Ficha Técnica", 
        "Registrar Orden de Compra",
        "Seguimiento de Órdenes",
        "Registrar Orden de Producción",
        "Órdenes de Producción",
        "Programar Producción"
        ])
    else:
        menu = st.sidebar.selectbox("Menú", ["Visualizar Ficha Técnica"])

# =======================
# CLIENTES
# =======================
    clientes_csv_path = "datos/clientes.csv"
    if os.path.exists(clientes_csv_path):
        clientes_df = pd.read_csv(clientes_csv_path)
        lista_clientes = clientes_df["Cliente"].tolist()
    else:
        clientes_df = pd.DataFrame(columns=["Cliente", "NIT", "Dirección", "Teléfono", "Correo",
                                            "Contacto1", "Correo1", "Contacto2", "Correo2"])
        lista_clientes = []

# =======================
# GESTIÓN DE CLIENTES
# =======================

    if menu == "Registrar Cliente" and st.session_state["rol"] == "Administrador":
       
        st.header("📋 Gestión de Clientes")

        clientes_csv_path = "datos/clientes.csv"
        columnas_requeridas = ["Cliente", "NIT", "Dirección", "Teléfono", "Correo",
                                "Contacto1", "Correo1", "Contacto2", "Correo2"]

        if os.path.exists(clientes_csv_path):
            clientes_df = pd.read_csv(clientes_csv_path)
            for col in columnas_requeridas:
                if col not in clientes_df.columns:
                    clientes_df[col] = ""
        else:
            clientes_df = pd.DataFrame(columns=columnas_requeridas)

        # Estado de edición y eliminación
        editar_nit = st.session_state.get("editar_nit", None)
        eliminar_nit = st.session_state.get("eliminar_nit", None)

        st.markdown("### 🔍 Buscar Cliente")
        filtro_busqueda = st.text_input("Buscar por nombre o NIT")

        st.markdown("### 📄 Clientes por página")
        clientes_por_pagina = st.selectbox("Clientes por página", [10, 20, 50], index=0)

        filtrado_df = clientes_df.copy()
        if filtro_busqueda:
            filtro = filtro_busqueda.lower()
            filtrado_df = clientes_df[clientes_df.apply(lambda row:
                filtro in str(row['Cliente']).lower() or filtro in str(row['NIT']), axis=1)]

        total_paginas = (len(filtrado_df) - 1) // clientes_por_pagina + 1
        pagina_actual = st.session_state.get("pagina_clientes", 1)
        pagina_actual = max(1, min(pagina_actual, total_paginas))

        start = (pagina_actual - 1) * clientes_por_pagina
        end = start + clientes_por_pagina
        pagina_df = filtrado_df.iloc[start:end]

        st.markdown("### 🗂️ Lista de Clientes")
        if not pagina_df.empty:
            for i, row in pagina_df.iterrows():
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 2, 2, 2, 2, 2, 0.5, 0.5])
                col1.write(row["Cliente"])
                col2.write(row["NIT"])
                col3.write(row["Dirección"])
                col4.write(row["Teléfono"])
                col5.write(row.get("Contacto1", ""))
                col6.write(row.get("Correo1", ""))
                if col7.button("✏️", key=f"editar_{row['NIT']}"):
                    st.session_state["editar_nit"] = row["NIT"]
                    st.session_state["mostrar_form"] = True
                    st.rerun()
                if col8.button("🗑️", key=f"eliminar_{row['NIT']}"):
                    st.session_state["eliminar_nit"] = row["NIT"]
                    st.rerun()
        else:
            st.info("No hay clientes registrados aún.")

        colpag1, colpag2, colpag3 = st.columns([1, 2, 1])
        with colpag1:
            if st.button("⬅️ Anterior") and pagina_actual > 1:
                st.session_state["pagina_clientes"] = pagina_actual - 1
                st.rerun()
        with colpag2:
            st.markdown(f"**Página {pagina_actual} de {total_paginas}**")
        with colpag3:
            if st.button("Siguiente ➡️") and pagina_actual < total_paginas:
                st.session_state["pagina_clientes"] = pagina_actual + 1
                st.rerun()

        # Confirmar eliminación
        if eliminar_nit:
            st.warning(f"¿Estás seguro de eliminar el cliente con NIT {eliminar_nit}?")
            confirmar = st.checkbox("☑️ Confirmar eliminación")
            if confirmar:
                clientes_df = clientes_df[clientes_df["NIT"] != eliminar_nit]
                clientes_df.to_csv(clientes_csv_path, index=False)
                st.success(f"Cliente con NIT {eliminar_nit} eliminado correctamente.")
                del st.session_state["eliminar_nit"]
                st.rerun()

        st.markdown("---")
        if st.button("➕ Registrar Cliente"):
            st.session_state["mostrar_form"] = True
            st.session_state["editar_nit"] = None

        if st.session_state.get("mostrar_form") or editar_nit:
            st.subheader("🧾 Formulario Cliente")

            if editar_nit:
                cliente_filtrado = clientes_df[clientes_df["NIT"] == editar_nit]
                if cliente_filtrado.empty:
                    st.warning(f"⚠️ El cliente con NIT {editar_nit} ya no existe.")
                    del st.session_state["editar_nit"]
                    st.rerun()
                else:
                    cliente_editar = cliente_filtrado.iloc[0]
            else:
                cliente_editar = pd.Series({col: "" for col in clientes_df.columns})

            with st.form("form_cliente"):
                nombre = st.text_input("Nombre del cliente", cliente_editar["Cliente"])
                nit = st.text_input("NIT", str(cliente_editar["NIT"]))
                direccion = st.text_input("Dirección", cliente_editar["Dirección"])
                telefono = st.text_input("Teléfono", str(cliente_editar["Teléfono"]))
                contacto1 = st.text_input("Contacto 1", cliente_editar["Contacto1"])
                correo1 = st.text_input("Correo contacto 1", cliente_editar["Correo1"])
                contacto2 = st.text_input("Contacto 2", cliente_editar["Contacto2"])
                correo2 = st.text_input("Correo contacto 2", cliente_editar["Correo2"])
                submitted = st.form_submit_button("💾 Guardar Cliente")

                if submitted:
                    if not all([nombre, nit, direccion, telefono, contacto1, correo1]):
                        st.error("⚠️ Todos los campos excepto Contacto 2 y Correo 2 son obligatorios.")
                    elif not nit.isdigit() or len(nit) != 10:
                        st.error("⚠️ El NIT debe tener 10 dígitos numéricos.")
                    elif not telefono.isdigit() or len(telefono) != 10:
                        st.error("⚠️ El teléfono debe tener 10 dígitos numéricos.")
                    elif "@" not in correo1 or "." not in correo1:
                        st.error("⚠️ Correo 1 no es válido.")
                    elif correo2 and ("@" not in correo2 or "." not in correo2):
                        st.error("⚠️ Correo 2 no es válido.")
                    elif nit in clientes_df["NIT"].astype(str).tolist() and nit != str(editar_nit):
                        st.error("⚠️ Ya existe otro cliente registrado con ese NIT.")
                    else:
                        nuevo_cliente = pd.DataFrame([{
                            "Cliente": nombre,
                            "NIT": nit,
                            "Dirección": direccion,
                            "Teléfono": telefono,
                            "Correo": "",  # Eliminado
                            "Contacto1": contacto1,
                            "Correo1": correo1,
                            "Contacto2": contacto2,
                            "Correo2": correo2
                        }])

                        if editar_nit:
                            clientes_df.loc[clientes_df["NIT"] == editar_nit, :] = nuevo_cliente.values
                            st.success("✅ Cliente actualizado correctamente.")
                        else:
                            clientes_df = pd.concat([clientes_df, nuevo_cliente], ignore_index=True)
                            st.success("✅ Cliente registrado correctamente.")

                        clientes_df.to_csv(clientes_csv_path, index=False)
                        st.session_state["mostrar_form"] = False
                        st.session_state["editar_nit"] = None
                        st.experimental_rerun()

# =======================
# REGISTRAR FICHA TÉCNICA
# =======================
    if menu == "Registrar Ficha Técnica" and st.session_state["rol"] == "Administrador":
        st.header("📄 Registrar Ficha Técnica")
        fichas_path = "datos/fichas_tecnicas.csv"
        if os.path.exists(fichas_path):
            fichas = pd.read_csv(fichas_path)
        else:
            fichas = pd.DataFrame()

        # Estado para reinicio
        if "ficha_guardada" not in st.session_state:
            st.session_state["ficha_guardada"] = False

        if st.session_state["ficha_guardada"]:
            st.success("✅ Ficha técnica guardada exitosamente.")
            if st.button("➕ Crear otra ficha"):
                for key in list(st.session_state.keys()):
                    if key.startswith("f_"):
                        del st.session_state[key]
                st.session_state["ficha_guardada"] = False
                st.rerun()
        else:
            st.subheader("📋 Datos generales")
            fecha = st.date_input("Fecha", value=date.today(), key="f_fecha")
            cliente = st.selectbox("Cliente", lista_clientes, key="f_cliente")
            referencia = st.text_input("Referencia", key="f_referencia")
            formula = st.text_input("Fórmula", key="f_formula")
            color = st.text_input("Color", key="f_color")
            laminado = st.number_input("Laminado (mm)", min_value=0.01, key="f_laminado")
            imagen = st.file_uploader("Imagen del producto (JPG/PNG)", type=["jpg", "jpeg", "png"], key="f_imagen")

            st.subheader("⚙️ Especificaciones técnicas")
            dureza = st.text_input("Dureza", key="f_dureza")
            temperatura = st.text_input("Temperatura (°C)", key="f_temp")
            presion = st.text_input("Presión (LB)", key="f_presion")
            peso = st.number_input("Peso del producto (gr)", min_value=0.5, key="f_peso")
            cavidades = st.number_input("Cavidades", min_value=1, key="f_cavidades")

            st.subheader("⏱️ Tiempos de proceso")
            tiempo_tacado = st.number_input("Tiempo de tacado (min)", min_value=1.00, step=0.1, key="f_tacado")
            tiempo_vulcanizado = st.number_input("Tiempo de vulcanizado (min)", min_value=0.50, step=0.1, key="f_vulcanizado")
            tiempo_total = tiempo_tacado + tiempo_vulcanizado
            promedio_hora = (60 / tiempo_total) * cavidades if tiempo_total > 0 else 0

            st.subheader("✂️ Corte")
            tiempo_corte = st.number_input("Tiempo de corte por unidad (min)", min_value=0.5, step=0.1, key="f_corte")
            cortadas_hora = 60 / tiempo_corte if tiempo_corte > 0 else 0
            jornada = st.number_input("Horas jornada", value=8, min_value=1, max_value=24, key="f_jornada")
            corte_dia = cortadas_hora * jornada

            st.subheader("📝 Observaciones")
            observaciones = st.text_area("Observaciones", key="f_obs")

            if st.button("💾 Guardar Ficha Técnica"):
                campos_texto = [referencia, formula, color, dureza, temperatura, presion]
                campos_numericos = [laminado, peso, cavidades, tiempo_tacado, tiempo_vulcanizado, tiempo_corte]

                if any(not c.strip() for c in campos_texto):
                    st.error("❌ Todos los campos de texto son obligatorios.")
                elif any(valor <= 0 for valor in campos_numericos):
                    st.error("❌ Todos los valores numéricos deben ser mayores a cero.")
                elif imagen is None:
                    st.error("❌ Debe adjuntar una imagen del producto.")
                else:
                    if "Versión" not in fichas.columns:
                        fichas["Versión"] = None
                    versiones = fichas[fichas["Referencia"] == referencia]["Versión"].tolist()
                    nueva_version = f"V{len(versiones)+1}"

                    # Guardar imagen
                    img_name = f"imagen_{referencia}_{nueva_version}.png"
                    with open(f"datos/{img_name}", "wb") as f:
                        f.write(imagen.read())

                    nueva_ficha = pd.DataFrame([{
                        "Referencia": referencia,
                        "Versión": nueva_version,
                        "Fecha": fecha,
                        "Cliente": cliente,
                        "Fórmula": formula,
                        "Color": color,
                        "Laminado": laminado,
                        "Imagen": img_name,
                        "Dureza": dureza,
                        "Temperatura": temperatura,
                        "Presión": presion,
                        "Peso": peso,
                        "Cavidades": cavidades,
                        "Tacado": tiempo_tacado,
                        "Vulcanizado": tiempo_vulcanizado,
                        "TiempoTotal": tiempo_total,
                        "PromedioHora": promedio_hora,
                        "TiempoCorteUnidad": tiempo_corte,
                        "CorteHora": cortadas_hora,
                        "CorteDiario": corte_dia,
                        "Jornada": jornada,
                        "Observaciones": observaciones
                    }])

                    fichas = pd.concat([fichas, nueva_ficha], ignore_index=True)
                    fichas.to_csv(fichas_path, index=False)

                    st.session_state["ficha_guardada"] = True
                    st.rerun()
            
# ==== Visualizar Ficha Técnica ====

    if "modo_version" not in st.session_state:
        st.session_state["modo_version"] = False
    
    if "ficha_guardada" not in st.session_state:
        st.session_state["ficha_guardada"] = False

    elif menu == "Visualizar Ficha Técnica":
        st.header("📁 Visualización de Fichas Técnicas")

        fichas_path = "datos/fichas_tecnicas.csv"
        if not os.path.exists(fichas_path):
            st.warning("No hay fichas técnicas registradas.")
            st.stop()

        fichas = pd.read_csv(fichas_path)
        fichas = fichas.dropna(subset=["Cliente", "Referencia", "Versión"])

        if fichas.empty:
            st.warning("No hay fichas válidas registradas.")
            st.stop()

        clientes = fichas["Cliente"].dropna().unique().tolist()
        cliente_sel = st.selectbox("Selecciona un cliente", clientes)

        fichas_cliente = fichas[fichas["Cliente"] == cliente_sel]
        referencias = fichas_cliente["Referencia"].dropna().unique().tolist()

        if not referencias:
            st.warning("Este cliente no tiene fichas técnicas registradas.")
            st.stop()

        referencia_sel = st.selectbox("Selecciona una referencia", referencias)
        ficha = fichas_cliente[fichas_cliente["Referencia"].str.lower() == referencia_sel.lower()]
        if ficha.empty:
            st.warning("⚠️ No hay ficha técnica registrada para esta referencia.")
            st.stop()

        ficha = ficha.sort_values("Versión", ascending=False).iloc[0]

# ENCABEZADO VISUAL
        st.markdown("---")
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image("https://i.imgur.com/9GU0T8B.png", width=100)
        with col2:
            st.markdown("## FICHA TÉCNICA DE PRODUCTO")
            st.markdown(f"**Versión:** {ficha['Versión']} | **Código ficha:** FTP-{ficha.name:03d}")

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**📅 Fecha:** {ficha['Fecha']}")
        col2.markdown(f"**🏢 Cliente:** {ficha['Cliente']}")
        col3.markdown(f"**🧪 Fórmula:** {ficha['Fórmula']}")

        st.markdown("---")
        st.markdown("### 📦 Especificaciones del Producto")
        col1, col2 = st.columns([1, 2])
        with col1:
            if ficha["Imagen"] and os.path.exists(f"datos/{ficha['Imagen']}"):
                st.image(f"datos/{ficha['Imagen']}", caption="Imagen del producto", width=200)
        with col2:
            st.markdown(f"**Referencia:** {ficha['Referencia']}")
            st.markdown(f"**Color:** {ficha['Color']}")
            st.markdown(f"**Laminado:** {ficha['Laminado']} mm")
            st.markdown(f"**Peso:** {ficha['Peso']} gr")
            st.markdown(f"**Dureza:** {ficha['Dureza']}")
            st.markdown(f"**Cavidades:** {ficha['Cavidades']}")

        st.markdown("---")
        st.markdown("### ⚙️ Especificaciones del Proceso")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Temperatura:** {ficha['Temperatura']}")
            st.markdown(f"**Presión:** {ficha['Presión']}")
            st.markdown(f"**Vulcanizado:** {ficha['Vulcanizado']} min")
        with col2:
            st.markdown(f"**Tacado:** {ficha['Tacado']} min")
            st.markdown(f"**Tiempo Total:** {ficha['TiempoTotal']} min")
            st.markdown(f"**Promedio por Hora:** {ficha['PromedioHora']:.2f} uds")

        st.markdown("---")
        st.markdown("### ✂️ Datos de Corte")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Tiempo por unidad:** {ficha['TiempoCorteUnidad']} min")
        with col2:
            st.markdown(f"**Corte por Hora:** {ficha['CorteHora']:.2f} uds")
            st.markdown(f"**Corte diario estimado:** {ficha['CorteDiario']:.2f} uds")

        st.markdown("---")
        st.markdown("### 📝 Observaciones")
        st.write(ficha["Observaciones"])

        if st.session_state["ficha_guardada"]:
            st.success("✅ Nueva versión registrada exitosamente.")
            st.session_state["ficha_guardada"] = False

 # ========= Generar Nueva Versión (solo administrador) =========
        if "modo_version" not in st.session_state:
            st.session_state["modo_version"] = False

        if st.session_state["rol"] == "Administrador":
            if not st.session_state["modo_version"]:
                if st.button("🔁 Generar nueva versión"):
                    st.session_state["modo_version"] = True
                    st.rerun()

        if st.session_state["modo_version"]:
            with st.form("nueva_version"):
                st.subheader("🆕 Crear nueva versión de ficha técnica")

                campos_editables = {}
                for campo in [
                    "Fórmula", "Color", "Laminado", "Dureza", "Temperatura", "Presión",
                    "Peso", "Cavidades", "Tacado", "Vulcanizado", "TiempoCorteUnidad",
                    "Jornada", "Observaciones"
                ]:
                    tipo = float if campo in [
                        "Laminado", "Peso", "TiempoCorteUnidad", "Tacado",
                        "Vulcanizado", "Cavidades", "Jornada"
                    ] else str
                    valor = ficha[campo]
                    nuevo = st.text_input(campo, str(valor)) if tipo == str else st.number_input(campo, value=float(valor), step=0.1)
                    campos_editables[campo] = nuevo

                nueva_imagen = st.file_uploader("📸 Nueva imagen (opcional)", type=["jpg", "jpeg", "png"])
                confirmar = st.checkbox("☑️ Confirmo que deseo guardar esta nueva versión")

                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 Guardar nueva versión")
                with col2:
                    cancelar = st.form_submit_button("❌ Cancelar")

                if cancelar:
                    st.session_state["modo_version"] = False
                    st.rerun()

                if submitted:
                    cambios = any(str(ficha[c]) != str(campos_editables[c]) for c in campos_editables)
                    if not confirmar:
                        st.error("⚠️ Debes confirmar que deseas guardar la nueva versión.")
                    elif not cambios and nueva_imagen is None:
                        st.error("⚠️ Para crear una nueva versión debes modificar al menos un campo o cargar una nueva imagen.")
                    else:
                        nuevas_versiones = fichas[fichas["Referencia"].str.lower() == ficha["Referencia"].lower()]
                        version_num = len(nuevas_versiones) + 1
                        nueva_version = f"V{version_num}"

                        imagen_nombre = ficha["Imagen"]
                        if nueva_imagen:
                            imagen_nombre = f"imagen_{ficha['Referencia']}_{nueva_version}.png"
                            with open(f"datos/{imagen_nombre}", "wb") as f:
                                f.write(nueva_imagen.read())

                        nueva_ficha = ficha.copy()
                        for campo, valor in campos_editables.items():
                            nueva_ficha[campo] = valor

                        nueva_ficha["TiempoTotal"] = float(nueva_ficha["Tacado"]) + float(nueva_ficha["Vulcanizado"])
                        nueva_ficha["PromedioHora"] = (60 / nueva_ficha["TiempoTotal"]) * float(nueva_ficha["Cavidades"])
                        nueva_ficha["CorteHora"] = 60 / float(nueva_ficha["TiempoCorteUnidad"])
                        nueva_ficha["CorteDiario"] = nueva_ficha["CorteHora"] * float(nueva_ficha["Jornada"])
                        nueva_ficha["Versión"] = nueva_version
                        nueva_ficha["Fecha"] = date.today()
                        nueva_ficha["Imagen"] = imagen_nombre

                        fichas = pd.concat([fichas, pd.DataFrame([nueva_ficha])], ignore_index=True)
                        fichas.to_csv(fichas_path, index=False)

                        st.session_state["ficha_guardada"] = True
                        st.session_state["modo_version"] = False
                        st.rerun()

# =======================
# VISUALIZAR ÓRDENES DE PRODUCCIÓN
# =======================
    elif menu == "Órdenes de Producción":
        st.header("🏭 Órdenes de Producción")
        st.subheader("🧾 Órdenes Generales")

        op_path = "datos/ordenes_produccion.csv"
        detalle_op_path = "datos/detalle_ordenes_produccion.csv"
        produccion_real_path = "datos/produccion_real.csv"
        oc_path = "datos/ordenes_compra.csv"  # para traer el número de OC del cliente

        if not all(os.path.exists(p) for p in [op_path, detalle_op_path, produccion_real_path, oc_path]):
            st.warning("No hay datos suficientes para mostrar órdenes de producción.")
            st.stop()

        op_df = pd.read_csv(op_path)
        detalle_op_df = pd.read_csv(detalle_op_path)
        produccion_real_df = pd.read_csv(produccion_real_path)
        ordenes_oc = pd.read_csv(oc_path)

        # Agregar el número de OC del cliente al detalle de OP
        detalle_op_df["OC_Origen"] = detalle_op_df["OC_Origen"].astype(str)
        ordenes_oc["Numero_OC_Cliente"] = ordenes_oc["Numero_OC_Cliente"].astype(str)
        
        detalle_op_df = detalle_op_df.merge(
            ordenes_oc[["ID_Orden", "Numero_OC_Cliente"]],
            left_on="OC_Origen",
            right_on="Numero_OC_Cliente",
            how="left"
        )

        # Agrupar producción real
        produccion_agrupada = produccion_real_df.groupby(["ID_OP", "Referencia"])["Cantidad_Producida"].sum().reset_index()

        # Unir con detalle OP
        detalle_completo = detalle_op_df.merge(
            produccion_agrupada,
            on=["ID_OP", "Referencia"],
            how="left"
        ).fillna({"Cantidad_Producida": 0})

        # Calcular avance global por OP
        avance_por_op = detalle_completo.groupby("ID_OP").apply(
            lambda x: (x["Cantidad_Producida"].sum() / x["Cantidad_Producir"].sum()) * 100 if x["Cantidad_Producir"].sum() > 0 else 0
        ).reset_index(name="Avance (%)")

        resumen = op_df.merge(avance_por_op, on="ID_OP", how="left").fillna({"Avance (%)": 0})

        for _, row in resumen.iterrows():
            with st.expander(f"🔹 {row['ID_OP']} | Cliente: {row['Cliente']} | Fecha: {row['Fecha_Creacion']}"):
                st.markdown(f"**Avance general:** {row['Avance (%)']:.2f}%")

                detalle_filtrado = detalle_completo[detalle_completo["ID_OP"] == row["ID_OP"]]

                # Agrupar referencias duplicadas en una sola línea
                detalle_filtrado = detalle_filtrado.groupby(
                    ["Referencia", "OC_Origen", "Fecha_Entrega"]
                ).agg({
                    "Cantidad_Producir": "sum",
                    "Cantidad_Producida": "sum"
                }).reset_index()

                # Eliminar duplicados por seguridad
                detalle_filtrado = detalle_filtrado.drop_duplicates(subset=["Referencia", "OC_Origen", "Fecha_Entrega", "Cantidad_Producir"])

                for _, det in detalle_filtrado.iterrows():
                    avance_ref = (det["Cantidad_Producida"] / det["Cantidad_Producir"]) * 100 if det["Cantidad_Producir"] > 0 else 0
                    st.markdown(
                        f"📦 Referencia: **{det['Referencia']}** | "
                        f"OC Cliente: {det['OC_Origen']} | "
                        f"Programado: {det['Cantidad_Producir']} uds | "
                        f"Producido: {int(det['Cantidad_Producida'])} uds | "
                        f"Avance: **{avance_ref:.2f}%** | "
                        f"Fecha Entrega: {det['Fecha_Entrega']}"
                    )

# =======================
# REGISTRAR ORDEN DE COMPRA
# =======================
    if menu == "Registrar Orden de Compra" and st.session_state["rol"] == "Administrador":
        st.header("📝 Registro de Orden de Compra")

        # Rutas de archivos
        ordenes_path = "datos/ordenes_compra.csv"
        detalles_path = "datos/detalle_ordenes_compra.csv"
        fichas_path = "datos/fichas_tecnicas.csv"

        # Cargar datos existentes
        ordenes_df = pd.read_csv(ordenes_path, dtype={"Numero_OC_Cliente": str})if os.path.exists(ordenes_path) else pd.DataFrame(columns=["ID_Orden", "Cliente", "Numero_OC_Cliente", "Fecha_Recepcion", "Estado"])
        detalles_df = pd.read_csv(detalles_path) if os.path.exists(detalles_path) else pd.DataFrame(columns=["ID_Orden", "Referencia", "Cantidad", "Fecha_Entrega", "Precio_Unitario"])
        fichas_df = pd.read_csv(fichas_path) if os.path.exists(fichas_path) else pd.DataFrame()

        # Generar nuevo ID incremental interno
        nuevo_id = ordenes_df["ID_Orden"].max() + 1 if not ordenes_df.empty else 1

        st.subheader("📋 Información General")
        cliente = st.selectbox("Cliente", lista_clientes)
        numero_oc_cliente = st.text_input("Número de Orden de Compra (cliente)")
        fecha_recepcion = st.date_input("Fecha de recepción", value=date.today())

        # Validar número de orden repetido para el mismo cliente
        if numero_oc_cliente and not st.session_state.get("productos_temp"):
            duplicada = (
                (ordenes_df["Cliente"] == cliente) &
                (ordenes_df["Numero_OC_Cliente"] == numero_oc_cliente)
            ).any()
            if duplicada:
                st.error(f"⚠️ Ya existe una orden de compra del cliente **{cliente}** con el número **{numero_oc_cliente}**.")
                st.stop()

        # Inicializar productos temporales
        if "productos_temp" not in st.session_state:
            st.session_state["productos_temp"] = []

        # Filtrar referencias del cliente
        referencias_disponibles = fichas_df[fichas_df["Cliente"] == cliente]["Referencia"].unique().tolist()
        if not referencias_disponibles:
            st.warning(f"⚠️ No hay productos registrados para el cliente **{cliente}**.")
            st.stop()

        with st.form("form_producto"):
            col1, col2, col3, col4 = st.columns([3, 2, 3, 2])
            with col1:
                referencia = st.selectbox("Referencia", referencias_disponibles, key="ref")
            with col2:
                cantidad = st.number_input("Cantidad", min_value=1, key="cant")
            with col3:
                fecha_entrega = st.date_input("Fecha de entrega", key="fecha_entrega")
            with col4:
                precio_unitario = st.number_input("Precio unitario", min_value=0.01, step=0.01, key="precio")

            agregar = st.form_submit_button("➕ Agregar producto")

            if agregar:
                if not numero_oc_cliente:
                    st.error("⚠️ Debes ingresar el número de orden de compra del cliente antes de agregar productos.")
                else:
                    duplicada = (
                        (ordenes_df["Cliente"] == cliente) &
                        (ordenes_df["Numero_OC_Cliente"] == numero_oc_cliente)
                    ).any()
                    if duplicada:
                        st.error(f"⚠️ Ya existe una orden de compra del cliente **{cliente}** con el número **{numero_oc_cliente}**.")
                    else:
                        st.session_state["productos_temp"].append({
                            "ID_Orden": nuevo_id,
                            "Referencia": referencia,
                            "Cantidad": cantidad,
                            "Fecha_Entrega": fecha_entrega,
                            "Precio_Unitario": precio_unitario
                        })
                        st.success(f"✅ Producto {referencia} agregado")
                        st.rerun()

        # Mostrar productos agregados
        if st.session_state["productos_temp"]:
            st.markdown("### 📦 Productos en esta orden")
            cols = st.columns([3, 1, 2, 2, 1])
            cols[0].markdown("**Referencia**")
            cols[1].markdown("**Cantidad**")
            cols[2].markdown("**Fecha Entrega**")
            cols[3].markdown("**Precio Unitario**")
            cols[4].markdown("**Eliminar**")

            for i, prod in enumerate(st.session_state["productos_temp"]):
                cols = st.columns([3, 1, 2, 2, 1])
                cols[0].markdown(prod["Referencia"])
                cols[1].markdown(str(prod["Cantidad"]))
                cols[2].markdown(str(prod["Fecha_Entrega"]))
                cols[3].markdown(f"${prod['Precio_Unitario']:.2f}")
                if cols[4].button("🗑️", key=f"del_{i}"):
                    st.session_state["productos_temp"].pop(i)
                    st.rerun()

            if st.button("🧹 Limpiar productos"):
                st.session_state["productos_temp"] = []
                st.rerun()

        # Registrar orden
            if st.button("✅ Registrar Orden de Compra") and st.session_state["productos_temp"]:
                if not numero_oc_cliente:
                    st.error("⚠️ Debes ingresar el número de orden de compra del cliente.")
                    st.stop()

                # Validar duplicado justo antes de registrar
                duplicada = (
                    (ordenes_df["Cliente"] == cliente) &
                    (ordenes_df["Numero_OC_Cliente"] == numero_oc_cliente)
                ).any()
                if duplicada:
                    st.error(f"⚠️ Ya existe una orden de compra del cliente **{cliente}** con el número **{numero_oc_cliente}**.")
                    st.stop()


                nueva_orden = pd.DataFrame([{
                    "ID_Orden": nuevo_id,
                    "Cliente": cliente,
                    "Numero_OC_Cliente": numero_oc_cliente,
                    "Fecha_Recepcion": fecha_recepcion,
                    "Estado": "Recibida"
                }])
                nuevos_detalles = pd.DataFrame(st.session_state["productos_temp"])

                ordenes_df = pd.concat([ordenes_df, nueva_orden], ignore_index=True)
                detalles_df = pd.concat([detalles_df, nuevos_detalles], ignore_index=True)

                ordenes_df.to_csv(ordenes_path, index=False)
                detalles_df.to_csv(detalles_path, index=False)

                st.success(f"✅ Orden de compra **{numero_oc_cliente}** registrada exitosamente.")
                st.session_state["productos_temp"] = []

            elif not st.session_state["productos_temp"]:
                st.info("Agrega al menos un producto para registrar la orden.")

# =======================
# SEGUIMIENTO DE ORDEN DE COMPRA
# =======================

    elif menu == "Seguimiento de Órdenes":
        st.header("📋 Seguimiento de Órdenes de Compra")

        ordenes_path = "datos/ordenes_compra.csv"
        detalles_path = "datos/detalle_ordenes_compra.csv"

        if not os.path.exists(ordenes_path) or not os.path.exists(detalles_path):
            st.warning("No hay órdenes registradas.")
        else:
            ordenes_df = pd.read_csv(ordenes_path, dtype={"Numero_OC_Cliente": str})
            detalles_df = pd.read_csv(detalles_path)

            # Inicializar columna Producido si no existe
            if "Producido" not in detalles_df.columns:
                detalles_df["Producido"] = 0
                detalles_df.to_csv(detalles_path, index=False)

            # Recalcular estado de cada orden en función del progreso
            for idx, orden in ordenes_df.iterrows():
                productos = detalles_df[detalles_df["ID_Orden"] == orden["ID_Orden"]]

                total_cantidad = productos["Cantidad"].sum()
                total_producido = productos["Producido"].sum()

                if total_producido == 0:
                    estado_actual = "Pendiente"
                elif total_producido < total_cantidad:
                    estado_actual = "En Producción"
                else:
                    estado_actual = "Terminada"

                ordenes_df.at[idx, "Estado"] = estado_actual

            # Guardar cambios en archivo CSV
            ordenes_df.to_csv(ordenes_path, index=False)
            st.subheader("🔎 Filtro por estado")
            estados = ordenes_df["Estado"].unique().tolist()
            estado_filtro = st.selectbox("Selecciona un estado", ["Todos"] + estados)

            if estado_filtro != "Todos":
                ordenes_df = ordenes_df[ordenes_df["Estado"] == estado_filtro]

            if ordenes_df.empty:
                st.info("No hay órdenes con el estado seleccionado.")
            else:
                st.markdown("### 🧾 Órdenes encontradas")
                for idx, orden in ordenes_df.iterrows():
                    productos = detalles_df[detalles_df["ID_Orden"] == orden["ID_Orden"]]

                    total_cantidad = productos["Cantidad"].sum()
                    total_producido = productos["Producido"].sum()
                    avance = total_producido / total_cantidad if total_cantidad > 0 else 0

                    with st.expander(f"🧾 {orden['Numero_OC_Cliente']} - {orden['Cliente']} ({avance*100:.1f}%)"):
                        col1, col2, col3, col4 = st.columns(4)
                        col1.markdown(f"**📅 Fecha recepción:** {orden['Fecha_Recepcion']}")
                        col2.markdown(f"**📌 Estado:** {orden['Estado']}")
                        col3.markdown(f"**🏢 Cliente:** {orden['Cliente']}")
                        col4.progress(avance)

                        st.markdown("#### 📦 Avance por referencia")
                        for i, row in productos.iterrows():
                            colr1, colr2, colr3 = st.columns([3, 2, 5])

                            referencia = row['Referencia']
                            producido = row['Producido'] if pd.notna(row['Producido']) else 0
                            cantidad = row['Cantidad'] if pd.notna(row['Cantidad']) else 0

                            # Calcular progreso con protección total
                            progreso = (producido / cantidad * 100) if cantidad > 0 else 0
                            progreso_valido = progreso / 100  # Streamlit espera 0.0 - 1.0

                            colr1.markdown(f"🔹 **{referencia}**")
                            colr2.markdown(f"{int(producido)}/{int(cantidad)} unidades")
                            colr3.progress(progreso_valido, text=f"{progreso:.1f}% completado")
                            
# ========================
# REGISTRAR ORDEN DE PRODUCCIÓN
# ========================
    elif menu == "Registrar Orden de Producción" and st.session_state["rol"] == "Administrador":
        st.header("🏭 Registrar Orden de Producción")

        op_path = "datos/ordenes_produccion.csv"
        detalle_op_path = "datos/detalle_ordenes_produccion.csv"
        oc_path = "datos/ordenes_compra.csv"
        detalle_oc_path = "datos/detalle_ordenes_compra.csv"

        if not os.path.exists(oc_path) or not os.path.exists(detalle_oc_path):
            st.warning("No hay órdenes de compra registradas.")
            st.stop()

        ordenes_oc = pd.read_csv(oc_path)
        detalle_oc = pd.read_csv(detalle_oc_path)

        # Validación permanente de columna Producido
        if "Producido" not in detalle_oc.columns:
            detalle_oc["Producido"] = 0
        else:
            detalle_oc["Producido"] = detalle_oc["Producido"].fillna(0)

        fichas_df = pd.read_csv("datos/fichas_tecnicas.csv")

        clientes_disponibles = ordenes_oc["Cliente"].unique().tolist()
        cliente_sel = st.selectbox("Selecciona el cliente", clientes_disponibles)

        ocs_cliente = ordenes_oc[ordenes_oc["Cliente"] == cliente_sel]
        detalle_cliente = detalle_oc[detalle_oc["ID_Orden"].isin(ocs_cliente["ID_Orden"])]
        detalle_cliente = detalle_cliente.merge(
            ordenes_oc[["ID_Orden", "Numero_OC_Cliente"]],
            on="ID_Orden", how="left"
        )
        detalle_cliente["Pendiente"] = detalle_cliente["Cantidad"] - detalle_cliente["Producido"]

        # Excluir combinaciones ya incluidas en una OP
        if os.path.exists(detalle_op_path):
            detalle_op_df = pd.read_csv(detalle_op_path)
            detalle_cliente["clave"] = (
                detalle_cliente["Referencia"].astype(str) + "|" +
                detalle_cliente["Numero_OC_Cliente"].astype(str) + "|" +
                detalle_cliente["Fecha_Entrega"].astype(str)
            )
            detalle_op_df["clave"] = (
                detalle_op_df["Referencia"].astype(str) + "|" +
                detalle_op_df["OC_Origen"].astype(str) + "|" +
                detalle_op_df["Fecha_Entrega"].astype(str)
            )
            detalle_cliente = detalle_cliente[~detalle_cliente["clave"].isin(detalle_op_df["clave"])]
            detalle_cliente.drop(columns="clave", inplace=True)

        detalle_cliente = detalle_cliente[detalle_cliente["Pendiente"] > 0]

        resumen = detalle_cliente.groupby(["Referencia", "Numero_OC_Cliente", "Fecha_Entrega"]).agg({
            "Pendiente": "sum"
        }).reset_index()

        if resumen.empty:
            st.subheader("📦 Referencias pendientes por generar una OP")
            st.success("✅ No hay referencias pendientes para generar OP.")
            st.stop()
        else:
            st.subheader("📦 Referencias pendientes por generar una OP")
            st.dataframe(resumen.rename(columns={"Numero_OC_Cliente": "OC"}))

        st.subheader("➕ Selección de referencias para producir")
        st.markdown("Selecciona las referencias que deseas producir. Por defecto se prellena el total pendiente.")

        with st.form("form_op"):
            seleccionadas = []
            for _, fila in resumen.iterrows():
                ref = fila["Referencia"]
                oc = fila["Numero_OC_Cliente"]
                fecha = fila["Fecha_Entrega"]
                pendiente = int(fila["Pendiente"])

                clave = f"{ref}_{oc}_{fecha}"
                col1, col2 = st.columns([4, 2])

                with col1:
                    seleccionado = st.checkbox(
                        f"🔹 {ref} (OC: {oc}, entrega: {fecha})",
                        key=f"check_{clave}"
                    )
                with col2:
                    cantidad = st.number_input(
                        "Cantidad a producir",
                        min_value=0,
                        max_value=pendiente,
                        value=pendiente if seleccionado else 0,
                        step=1,
                        key=f"input_{clave}",
                        disabled=not seleccionado
                    )

                if seleccionado and cantidad > 0:
                    seleccionadas.append({
                        "Referencia": ref,
                        "Cantidad_Seleccionada": cantidad,
                        "OC": oc,
                        "Fecha_Entrega": fecha
                    })

            submit_op = st.form_submit_button("✅ Registrar Orden de Producción")

            if submit_op:
                if not seleccionadas:
                    st.warning("⚠️ Debes seleccionar al menos una referencia con cantidad mayor a cero.")
                    st.stop()

                op_df = pd.read_csv(op_path) if os.path.exists(op_path) else pd.DataFrame(columns=["ID_OP", "Cliente", "Fecha_Creacion", "Estado"])
                nuevo_id = f"OP-{len(op_df)+1:04d}"
                nueva_op = pd.DataFrame([{
                    "ID_OP": nuevo_id,
                    "Cliente": cliente_sel,
                    "Fecha_Creacion": date.today(),
                    "Estado": "En proceso"
                }])
                op_df = pd.concat([op_df, nueva_op], ignore_index=True)
                op_df.to_csv(op_path, index=False)

                detalle_op_df = pd.read_csv(detalle_op_path) if os.path.exists(detalle_op_path) else pd.DataFrame(columns=[
                    "ID_OP", "Referencia", "Cantidad_Producir", "OC_Origen", "Cantidad_OC", "Fecha_Entrega"
                ])

                nuevas_lineas = []
                for item in seleccionadas:
                    ref = item["Referencia"]
                    cantidad_total = item["Cantidad_Seleccionada"]
                    oc = item["OC"]
                    fecha_entrega = item["Fecha_Entrega"]

                    ref_detalle = detalle_cliente[
                        (detalle_cliente["Referencia"] == ref) &
                        (detalle_cliente["Numero_OC_Cliente"] == oc) &
                        (detalle_cliente["Fecha_Entrega"] == fecha_entrega)
                    ].sort_values("Fecha_Entrega")

                    restante = cantidad_total
                    for _, fila in ref_detalle.iterrows():
                        if restante <= 0:
                            break
                        cantidad_oc = min(fila["Pendiente"], restante)
                        nuevas_lineas.append({
                            "ID_OP": nuevo_id,
                            "Referencia": ref,
                            "Cantidad_Producir": cantidad_oc,
                            "OC_Origen": oc,
                            "Cantidad_OC": fila["Cantidad"],
                            "Fecha_Entrega": fecha_entrega
                        })
                        restante -= cantidad_oc

                detalle_op_df = pd.concat([detalle_op_df, pd.DataFrame(nuevas_lineas)], ignore_index=True)
                detalle_op_df.to_csv(detalle_op_path, index=False)

                st.success(f"✅ Orden de Producción **{nuevo_id}** registrada exitosamente.")
                st.info("Redirigiendo en 3 segundos...")
                time.sleep(3)
                st.rerun()

# --------------------
# PROGRAMAR PRODUCCIÓN
# --------------------

    elif menu == "Programar Producción":
        st.markdown("""
            <style>
            [data-testid="stSidebar"] ~ div .block-container {
                max-width: 100% !important;
                padding-left: 2rem;
                padding-right: 2rem;
            }
            </style>
        """, unsafe_allow_html=True)

        st.header("📅 Programación de Producción (Asignación por Día)")

        maquinas_path = "datos/maquinas.csv"
        usuarios_path = "datos/usuarios.csv"
        op_path = "datos/ordenes_produccion.csv"
        detalle_op_path = "datos/detalle_ordenes_produccion.csv"
        programacion_path = "datos/programacion_produccion.csv"

        for path in [maquinas_path, usuarios_path, op_path, detalle_op_path]:
            if not os.path.exists(path):
                st.error(f"❌ Falta el archivo: {path}")
                st.stop()

        maquinas_df = pd.read_csv(maquinas_path)
        usuarios_df = pd.read_csv(usuarios_path)
        operarios_df = usuarios_df[usuarios_df["rol"] == "Operario"]
        op_df = pd.read_csv(op_path)
        detalle_op_df = pd.read_csv(detalle_op_path)

        referencias = detalle_op_df.merge(op_df, on="ID_OP", how="left")
        referencias = referencias.groupby(["ID_OP", "Cliente", "Referencia", "OC_Origen", "Fecha_Entrega"], as_index=False).agg({"Cantidad_Producir": "sum"})
        referencias_disponibles = referencias["Referencia"].dropna().unique().tolist()

        if "planificacion_tmp" not in st.session_state:
            st.session_state.planificacion_tmp = []
        if "planificacion_definitiva" not in st.session_state:
            st.session_state.planificacion_definitiva = []

        # === SELECCION DE FECHA ===
        fecha_dia = st.date_input("📅 Selecciona el día a programar", value=st.session_state.get("fecha_dia"))
        if fecha_dia is None:
            st.info("👈 Selecciona un nuevo día para continuar programando.")
        else:
            st.session_state["fecha_dia"] = fecha_dia
            fecha_str = fecha_dia.strftime("%Y-%m-%d")
            st.subheader(f"🧾 Asignaciones para el día {fecha_str}")

            if st.button("➕ Nueva asignación"):
                st.session_state.planificacion_tmp.append({
                    "Fecha": fecha_str,
                    "Máquina": "",
                    "Referencia": "",
                    "Operario": "",
                    "Hora_Inicio": None,
                    "Hora_Fin": None
                })

            asignaciones_actuales = [fila for fila in st.session_state.planificacion_tmp if fila["Fecha"] == fecha_str]
            eliminar_indices = []

            for i, fila in enumerate(asignaciones_actuales):
                col0, col1, col2, col3, col4, col5, col6 = st.columns([0.3, 2.5, 3, 2.5, 1.5, 1.5, 0.5], gap="small")
                with col0:
                    st.markdown(f"**{i+1}**")

                fila["Máquina"] = col1.selectbox("Máquina", maquinas_df["Nombre"].tolist(), index=maquinas_df["Nombre"].tolist().index(fila["Máquina"]) if fila["Máquina"] in maquinas_df["Nombre"].tolist() else 0, key=f"maq_{i}")
                fila["Referencia"] = col2.selectbox("Referencia", referencias_disponibles, index=referencias_disponibles.index(fila["Referencia"]) if fila["Referencia"] in referencias_disponibles else 0, key=f"ref_{i}")
                fila["Operario"] = col3.selectbox("Operario", operarios_df["nombre"].tolist(), index=operarios_df["nombre"].tolist().index(fila["Operario"]) if fila["Operario"] in operarios_df["nombre"].tolist() else 0, key=f"ope_{i}")
                fila["Hora_Inicio"] = col4.time_input("Hora Inicio", value=fila["Hora_Inicio"] if fila["Hora_Inicio"] else dtime(8, 0), key=f"ini_{i}")
                fila["Hora_Fin"] = col5.time_input("Hora Fin", value=fila["Hora_Fin"] if fila["Hora_Fin"] else dtime(17, 0), key=f"fin_{i}")

                if col6.button("🗑️", key=f"del_{i}"):
                    eliminar_indices.append(i)

            for idx in sorted(eliminar_indices, reverse=True):
                del st.session_state.planificacion_tmp[idx]

            if st.button("✅ Asignar este día"):
                plan_dia = [fila for fila in st.session_state.planificacion_tmp if fila["Fecha"] == fecha_str]

                errores = []
                for i, fila_i in enumerate(plan_dia):
                    for campo in ["Máquina", "Referencia", "Operario", "Hora_Inicio", "Hora_Fin"]:
                        if not fila_i[campo]:
                            errores.append(f"❌ La fila {i+1} tiene el campo '{campo}' vacío.")

                    if fila_i["Hora_Inicio"] and fila_i["Hora_Fin"] and fila_i["Hora_Inicio"] >= fila_i["Hora_Fin"]:
                        errores.append(f"🕒 La hora de inicio debe ser menor que la hora de fin en la fila {i+1}.")

                    for j, fila_j in enumerate(plan_dia):
                        if i >= j:
                            continue

                        overlap = not (fila_i["Hora_Fin"] <= fila_j["Hora_Inicio"] or fila_j["Hora_Fin"] <= fila_i["Hora_Inicio"])

                        if overlap:
                            if fila_i["Operario"] == fila_j["Operario"]:
                                errores.append(f"👷‍♂️ El operario {fila_i['Operario']} tiene solapamiento horario entre máquinas en filas {i+1} y {j+1}.")
                            if fila_i["Máquina"] == fila_j["Máquina"]:
                                errores.append(f"🛠️ La máquina {fila_i['Máquina']} tiene solapamiento horario en filas {i+1} y {j+1}.")

                if errores:
                    for e in errores:
                        st.error(e)
                    st.stop()

                for nueva in plan_dia:
                    if nueva not in st.session_state.planificacion_definitiva:
                        st.session_state.planificacion_definitiva.append(nueva)

                st.session_state.planificacion_tmp = [fila for fila in st.session_state.planificacion_tmp if fila["Fecha"] != fecha_str]
                st.success("✅ Asignaciones guardadas para el día actual.")

                # Resetear la fecha y refrescar
                if "fecha_dia" in st.session_state:
                    del st.session_state["fecha_dia"]
                    st.rerun()

        # === MOSTRAR PLANIFICACIÓN ACUMULADA SIEMPRE ===
        st.markdown("### 📋 Planificación acumulada (sin guardar)")

        df_acumulado = pd.DataFrame(st.session_state.planificacion_definitiva)

        if not df_acumulado.empty:
            df_acumulado = df_acumulado.sort_values(by=["Fecha", "Máquina", "Hora_Inicio"])
            st.dataframe(df_acumulado, use_container_width=True)

                    # Botón para guardar planificación definitiva con validaciones completas
        st.markdown("---")
        st.subheader("💾 Guardar programación definitiva")

        if st.button("💾 Guardar programación definitiva"):
            errores = []
            df_validado = df_acumulado.copy()

            for i, fila_i in df_validado.iterrows():
                for campo in ["Fecha", "Máquina", "Referencia", "Operario", "Hora_Inicio", "Hora_Fin"]:
                    if pd.isna(fila_i[campo]) or fila_i[campo] == "":
                        errores.append(f"❌ La fila {i+1} tiene el campo '{campo}' vacío.")

                if fila_i["Hora_Inicio"] >= fila_i["Hora_Fin"]:
                    errores.append(f"🕒 La hora de inicio debe ser menor que la de fin en la fila {i+1}.")

                for j, fila_j in df_validado.iterrows():
                    if i >= j or fila_i["Fecha"] != fila_j["Fecha"]:
                        continue

                    ini_i, fin_i = fila_i["Hora_Inicio"], fila_i["Hora_Fin"]
                    ini_j, fin_j = fila_j["Hora_Inicio"], fila_j["Hora_Fin"]

                    overlap = not (fin_i <= ini_j or fin_j <= ini_i)

                    if overlap:
                        if fila_i["Operario"] == fila_j["Operario"]:
                            errores.append(f"👷‍♂️ El operario {fila_i['Operario']} tiene solapamiento el {fila_i['Fecha']} entre filas {i+1} y {j+1}.")
                        if fila_i["Máquina"] == fila_j["Máquina"]:
                            errores.append(f"🛠️ La máquina {fila_i['Máquina']} tiene solapamiento el {fila_i['Fecha']} entre filas {i+1} y {j+1}.")

                similares = df_validado[
                    (df_validado["Fecha"] == fila_i["Fecha"]) &
                    (df_validado["Máquina"] == fila_i["Máquina"]) &
                    (df_validado["Operario"] == fila_i["Operario"]) &
                    (df_validado["Referencia"] == fila_i["Referencia"]) &
                    (df_validado.index != i)
                ]
                for _, fila_j in similares.iterrows():
                    if fila_j["Hora_Fin"] == fila_i["Hora_Inicio"]:
                        errores.append(f"🔁 Franja continua sospechosa en {fila_i['Fecha']} para máquina {fila_i['Máquina']} y operario {fila_i['Operario']}. Considera unirlas.")

            if errores:
                for e in errores:
                    st.error(e)
                st.stop()

            # Guardar en CSV
            if os.path.exists(programacion_path):
                df_guardado = pd.read_csv(programacion_path)
                if "Hora_Inicio" in df_guardado.columns:
                    df_guardado["Hora_Inicio"] = pd.to_datetime(df_guardado["Hora_Inicio"], errors="coerce").dt.strftime("%H:%M")
                    df_guardado["Hora_Fin"] = pd.to_datetime(df_guardado["Hora_Fin"], errors="coerce").dt.strftime("%H:%M")
            else:
                df_guardado = pd.DataFrame(columns=df_validado.columns)

            df_nuevo = df_validado.copy()
            df_nuevo["Hora_Inicio"] = df_nuevo["Hora_Inicio"].astype(str)
            df_nuevo["Hora_Fin"] = df_nuevo["Hora_Fin"].astype(str)

            df_final = pd.concat([df_guardado, df_nuevo], ignore_index=True)
            df_final.drop_duplicates(subset=["Fecha", "Máquina", "Hora_Inicio", "Hora_Fin"], keep="last", inplace=True)
            df_final.to_csv(programacion_path, index=False)

            st.success("✅ Programación guardada exitosamente.")
            st.session_state.planificacion_definitiva.clear()

