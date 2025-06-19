import streamlit as st
import pandas as pd
import os
from datetime import date

# Crear carpeta de datos
if not os.path.exists("datos"):
    os.makedirs("datos")

# =======================
# LOGIN CON SESIÓN
# =======================
def login():
    st.title("🔐 Iniciar sesión")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        try:
            #st.write("Directorio actual:", os.getcwd())
            df_usuarios = pd.read_csv("datos/usuarios.csv")
            #st.write("Columnas:", df_usuarios.columns)

            usuario = usuario.strip()
            clave = clave.strip()

            df_usuarios["usuario"] = df_usuarios["usuario"].astype(str).str.strip()
            df_usuarios["clave"] = df_usuarios["clave"].astype(str).str.strip()

            user = df_usuarios[(df_usuarios["usuario"] == usuario) & (df_usuarios["clave"] == clave)]
            #st.write("Usuario encontrado:", user)

            if not user.empty:
                st.session_state["logueado"] = True
                st.session_state["usuario"] = usuario
                st.session_state["rol"] = user.iloc[0]["rol"]
                st.success("Login exitoso. Redirigiendo...")
                st.rerun()
            else:
                st.error("Credenciales inválidas.")
        except Exception as e:
            st.error(f"Error al acceder al archivo de usuarios: {e}")

# Inicializar sesión
if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    login()
    st.stop()

# =======================
# MENÚ
# =======================
st.sidebar.success(f"Usuario: {st.session_state['usuario']} ({st.session_state['rol']})")
rol = st.session_state["rol"]

if rol == "Administrador":
    menu = st.sidebar.selectbox("Menú", ["Registrar Cliente", "Registrar Ficha Técnica", "Visualizar Ficha Técnica"])
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
if menu == "Registrar Cliente" and rol == "Administrador":
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
if menu == "Registrar Ficha Técnica" and rol == "Administrador":
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

# =======================
# VISUALIZAR FICHA TÉCNICA
# =======================
if menu == "Visualizar Ficha Técnica":
    st.header("📂 Visualización de Fichas Técnicas")
    try:
        fichas = pd.read_csv("datos/fichas_tecnicas.csv")
        referencias = fichas["Referencia"].unique().tolist()
        referencia_sel = st.selectbox("Selecciona una referencia", referencias)

        if rol == "Administrador":
            versiones = fichas[fichas["Referencia"] == referencia_sel]["Versión"].tolist()
            version_sel = st.selectbox("Selecciona una versión", versiones)
            ficha = fichas[(fichas["Referencia"] == referencia_sel) & (fichas["Versión"] == version_sel)].iloc[0]
        else:
            ficha = fichas[fichas["Referencia"] == referencia_sel].sort_values("Versión", ascending=False).iloc[-1]

        st.subheader(f"📘 Ficha Técnica - {ficha['Referencia']} {ficha['Versión']}")
        st.markdown(
            f"**Cliente:** {ficha['Cliente']}  \n"
            f"**Fecha:** {ficha['Fecha']}  \n"
            f"**Color:** {ficha['Color']}  \n"
            f"**Fórmula:** {ficha['Fórmula']}"
        )
        st.markdown(
            f"**Dureza:** {ficha['Dureza']}  \n"
            f"**Presión:** {ficha['Presión']}  \n"
            f"**Temperatura:** {ficha['Temperatura']}  \n"
            f"**Peso:** {ficha['Peso']} gr  \n"
            f"**Cavidades:** {ficha['Cavidades']}"
        )
        st.markdown(
            f"**Tacado:** {ficha['Tacado']} min  \n"
            f"**Vulcanizado:** {ficha['Vulcanizado']} min  \n"
            f"**Total:** {ficha['TiempoTotal']} min"
        )
        st.markdown(
            f"**Promedio Hora:** {ficha['PromedioHora']:.2f} uds  \n"
            f"**Corte por unidad:** {ficha['TiempoCorteUnidad']} min"
        )
        st.markdown(
            f"**Corte por hora:** {ficha['CorteHora']:.2f} uds  \n"
            f"**Corte diario:** {ficha['CorteDiario']:.2f} uds"
        )

        if ficha["Imagen"] and os.path.exists(f"datos/{ficha['Imagen']}"):
            st.image(f"datos/{ficha['Imagen']}", caption="Imagen del producto", width=300)

        st.subheader("📝 Observaciones")
        st.write(ficha["Observaciones"])

    except Exception as e:
        st.warning("No hay fichas registradas.")
        st.text(str(e))
