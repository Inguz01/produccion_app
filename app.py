import streamlit as st
import pandas as pd
import os
from datetime import date

# Crear carpeta de datos si no existe
if not os.path.exists("datos"):
    os.makedirs("datos")

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
        menu = st.sidebar.selectbox("Menú", ["Registrar Cliente", 
        "Registrar Ficha Técnica", 
        "Visualizar Ficha Técnica", 
        "Registrar Orden de Compra",
        "Seguimiento de Órdenes"])
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
    # REGISTRAR CLIENTE
    # =======================
    if menu == "Registrar Cliente" and st.session_state["rol"] == "Administrador":
        st.header("🧾 Registro de Cliente")
        with st.form("cliente_form"):
            nombre = st.text_input("Nombre del cliente")
            nit = st.text_input("NIT")
            direccion = st.text_input("Dirección")
            telefono = st.text_input("Teléfono")
            correo = st.text_input("Correo empresa")
            contacto1 = st.text_input("Contacto 1")
            correo1 = st.text_input("Correo contacto 1")
            contacto2 = st.text_input("Contacto 2")
            correo2 = st.text_input("Correo contacto 2")
            submitted = st.form_submit_button("Guardar Cliente")
        if submitted:
            nuevo_cliente = pd.DataFrame([[nombre, nit, direccion, telefono, correo,
                                            contacto1, correo1, contacto2, correo2]],
                                            columns=clientes_df.columns)
            clientes_df = pd.concat([clientes_df, nuevo_cliente], ignore_index=True)
            clientes_df.to_csv(clientes_csv_path, index=False)
            st.success(f"Cliente '{nombre}' guardado correctamente.")

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

        st.subheader("📋 Datos generales")
        fecha = st.date_input("Fecha", value=date.today())
        cliente = st.selectbox("Cliente", lista_clientes) if lista_clientes else st.text_input("Cliente")
        referencia = st.text_input("Referencia")
        formula = st.text_input("Fórmula")
        color = st.text_input("Color")
        laminado = st.number_input("Laminado (mm)", min_value=0.0)
        imagen = st.file_uploader("Imagen del producto (JPG/PNG)", type=["jpg", "jpeg", "png"])

        st.subheader("⚙️ Especificaciones técnicas")
        dureza = st.text_input("Dureza")
        temperatura = st.text_input("Temperatura (°C)")
        presion = st.text_input("Presión (LB)")
        peso = st.number_input("Peso del producto (gr)", min_value=1.0)
        cavidades = st.number_input("Cavidades", min_value=1)

        st.subheader("⏱️ Tiempos de proceso")
        tiempo_tacado = st.number_input("Tiempo de tacado (min)", step=0.1)
        tiempo_vulcanizado = st.number_input("Tiempo de vulcanizado (min)", step=0.1)
        tiempo_total = tiempo_tacado + tiempo_vulcanizado
        promedio_hora = (60 / tiempo_total) * cavidades if tiempo_total > 0 else 0

        st.subheader("✂️ Corte")
        tiempo_corte = st.number_input("Tiempo de corte por unidad (min)", step=0.1)
        cortadas_hora = 60 / tiempo_corte if tiempo_corte > 0 else 0
        jornada = st.number_input("Horas jornada", value=8, min_value=1, max_value=24)
        corte_dia = cortadas_hora * jornada

        st.subheader("📝 Observaciones")
        observaciones = st.text_area("Observaciones")

        if st.button("Guardar Ficha Técnica"):
            # Validar referencia y versión
            if "Versión" not in fichas.columns:
                fichas["Versión"] = None
            versiones = fichas[fichas["Referencia"] == referencia]["Versión"].tolist()
            nueva_version = f"V{len(versiones)+1}"

            # Guardar imagen
            img_name = f"imagen_{referencia}_{nueva_version}.png"
            if imagen:
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
                "Imagen": img_name if imagen else "",
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
            st.success(f"Ficha técnica {referencia} {nueva_version} guardada correctamente.")
            
    # ==== Visualizar Ficha Técnica ====
    elif menu == "Visualizar Ficha Técnica":
        st.header("📁 Visualización de Fichas Técnicas")
        fichas_path = "datos/fichas_tecnicas.csv"
        if not os.path.exists(fichas_path):
            st.warning("No hay fichas técnicas registradas.")
        else:
            fichas = pd.read_csv(fichas_path)

            if fichas.empty:
                st.warning("No hay fichas registradas.")
            else:
                clientes = fichas["Cliente"].unique().tolist()
                cliente_sel = st.selectbox("Selecciona un cliente", clientes)

                fichas_cliente = fichas[fichas["Cliente"] == cliente_sel]
                referencias = fichas_cliente["Referencia"].unique().tolist()
                referencia_sel = st.selectbox("Selecciona una referencia", referencias)

                # Filtrar por referencia y mostrar última versión
                ficha = fichas_cliente[fichas_cliente["Referencia"] == referencia_sel]
                ficha = ficha.sort_values("Versión", ascending=False).iloc[0]

                # ENCABEZADO
                st.markdown("---")
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.image("https://i.imgur.com/9GU0T8B.png", width=100)  # Reemplaza con tu logo si es local
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

# =======================
# REGISTRAR ORDEN DE COMPRA
# =======================
    if menu == "Registrar Orden de Compra" and st.session_state["rol"] == "Administrador":
        st.header("📝 Registro de Orden de Compra")

        # Archivos CSV
        ordenes_path = "datos/ordenes_compra.csv"
        detalles_path = "datos/detalle_ordenes_compra.csv"
        fichas_path = "datos/fichas_tecnicas.csv"

        # Cargar datos existentes
        ordenes_df = pd.read_csv(ordenes_path) if os.path.exists(ordenes_path) else pd.DataFrame(columns=["ID_Orden", "Cliente", "Fecha_Recepcion", "Estado"])
        detalles_df = pd.read_csv(detalles_path) if os.path.exists(detalles_path) else pd.DataFrame(columns=["ID_Orden", "Referencia", "Cantidad", "Fecha_Entrega", "Precio_Unitario"])
        fichas_df = pd.read_csv(fichas_path) if os.path.exists(fichas_path) else pd.DataFrame()

        # Generar nuevo ID de orden
        nuevo_id = f"OC-{len(ordenes_df) + 1:04d}"

        st.subheader("📋 Información General")
        cliente = st.selectbox("Cliente", lista_clientes)

        # Mantener cliente fijo una vez agregue productos
        if "cliente_orden" not in st.session_state:
            st.session_state["cliente_orden"] = cliente

        if st.session_state.get("productos_temp") and cliente != st.session_state["cliente_orden"]:
            st.warning("⚠️ No puedes cambiar el cliente una vez agregaste productos.")
            cliente = st.session_state["cliente_orden"]

        fecha_recepcion = st.date_input("Fecha de recepción", value=date.today())

        # Inicializar almacenamiento temporal
        if "productos_temp" not in st.session_state:
            st.session_state["productos_temp"] = []

        # Filtrar productos disponibles para ese cliente
        referencias_disponibles = fichas_df[fichas_df["Cliente"] == cliente]["Referencia"].unique().tolist()

        if not referencias_disponibles:
            st.warning(f"⚠️ No hay productos registrados para el cliente **{cliente}**. Crea primero una ficha técnica.")
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
                precio_unitario = st.number_input("Precio unitario", min_value=0.0, step=0.01, key="precio")

            agregar = st.form_submit_button("➕ Agregar producto")
            if agregar:
                st.session_state["productos_temp"].append({
                    "ID_Orden": nuevo_id,
                    "Referencia": referencia,
                    "Cantidad": cantidad,
                    "Fecha_Entrega": fecha_entrega,
                    "Precio_Unitario": precio_unitario
                })
                st.success(f"✅ Producto {referencia} agregado")
                st.session_state["cliente_orden"] = cliente
                st.rerun()

# Mostrar productos agregados
        if st.session_state["productos_temp"]:
            st.markdown("### 📦 Productos en esta orden")

            # Estilo CSS para tabla y botón
            st.markdown("""
                <style>
                .btn-small {
                    padding: 6px 10px;
                    font-size: 14px;
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                }
                .btn-small:hover {
                    background-color: #2563eb;
                }
                </style>
            """, unsafe_allow_html=True)

            # Mostrar encabezado con columnas
            cols = st.columns([3, 1, 2, 2, 1])
            cols[0].markdown("**Referencia**")
            cols[1].markdown("**Cantidad**")
            cols[2].markdown("**Fecha de Entrega**")
            cols[3].markdown("**Precio Unitario**")
            cols[4].markdown("**Eliminar**")

            for i, producto in enumerate(st.session_state["productos_temp"]):
                cols = st.columns([3, 1, 2, 2, 1])
                cols[0].markdown(producto["Referencia"])
                cols[1].markdown(str(producto["Cantidad"]))
                cols[2].markdown(str(producto["Fecha_Entrega"]))
                cols[3].markdown(f"${producto['Precio_Unitario']:.2f}")
                if cols[4].button("🗑️", key=f"eliminar_{i}"):
                    st.session_state["productos_temp"].pop(i)
                    st.rerun()

            # Botón para limpiar toda la lista
            if st.button("🧹 Limpiar productos"):
                st.session_state["productos_temp"] = []
                st.rerun()


        # Registrar orden (solo si hay productos)
        if st.button("✅ Registrar Orden de Compra") and st.session_state["productos_temp"]:
            nueva_orden = pd.DataFrame([{
                "ID_Orden": nuevo_id,
                "Cliente": cliente,
                "Fecha_Recepcion": fecha_recepcion,
                "Estado": "Recibida"
            }])
            nuevos_detalles = pd.DataFrame(st.session_state["productos_temp"])

            # Guardar
            ordenes_df = pd.concat([ordenes_df, nueva_orden], ignore_index=True)
            detalles_df = pd.concat([detalles_df, nuevos_detalles], ignore_index=True)

            ordenes_df.to_csv(ordenes_path, index=False)
            detalles_df.to_csv(detalles_path, index=False)

            st.success(f"Orden de compra **{nuevo_id}** registrada exitosamente.")
            st.session_state["productos_temp"] = []
            st.session_state["cliente_orden"] = ""
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
            ordenes_df = pd.read_csv(ordenes_path)
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

                    with st.expander(f"🧾 {orden['ID_Orden']} - {orden['Cliente']} ({avance*100:.1f}%)"):
                        col1, col2, col3, col4 = st.columns(4)
                        col1.markdown(f"**📅 Fecha recepción:** {orden['Fecha_Recepcion']}")
                        col2.markdown(f"**📌 Estado:** {orden['Estado']}")
                        col3.markdown(f"**🏢 Cliente:** {orden['Cliente']}")
                        col4.progress(avance)

                        st.markdown("#### 📦 Avance por referencia")
                        for i, row in productos.iterrows():
                            colr1, colr2, colr3 = st.columns([3, 2, 5])
                            colr1.markdown(f"🔹 **{row['Referencia']}**")
                            colr2.markdown(f"{int(row['Producido'])}/{int(row['Cantidad'])} unidades")
                            progreso = row["Producido"] / row["Cantidad"] if row["Cantidad"] > 0 else 0
                            colr3.progress(progreso, text=
                                "✅ Completado" if progreso >= 1 else 
                                "🔧 En proceso" if progreso > 0 else 
                                "⏳ Pendiente"
                            )
