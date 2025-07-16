import streamlit as st
import pandas as pd
import os
import time

# =========================
# CONFIGURACIÓN DE CARPETAS
# =========================
BASE_DIR = "datos"
CLIENTES_DIR = os.path.join(BASE_DIR, "clientes")
FICHAS_DIR = os.path.join(BASE_DIR, "fichas_tecnicas")
OC_DIR = os.path.join(BASE_DIR, "ordenes_compra")
OP_DIR = os.path.join(BASE_DIR, "ordenes_produccion")
PROG_DIR = os.path.join(BASE_DIR, "programacion")
IMG_DIR = os.path.join(FICHAS_DIR, "imagenes")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

for folder in [CLIENTES_DIR, FICHAS_DIR, OC_DIR, OP_DIR, PROG_DIR, IMG_DIR, CONFIG_DIR]:
    os.makedirs(folder, exist_ok=True)

# Archivos con rutas organizadas
clientes_csv_path = os.path.join(CLIENTES_DIR, "clientes.csv")
fichas_path = os.path.join(FICHAS_DIR, "fichas_tecnicas.csv")
ordenes_path = os.path.join(OC_DIR, "ordenes.csv")
detalles_path = os.path.join(OC_DIR, "detalles.csv")
op_path = os.path.join(OP_DIR, "ordenes_produccion.csv")
detalle_op_path = os.path.join(OP_DIR, "detalles_op.csv")
programacion_path = os.path.join(PROG_DIR, "programacion.csv")
produccion_real_path = os.path.join(PROG_DIR, "produccion_real.csv")
usuarios_path = os.path.join(CONFIG_DIR, "usuarios.csv")
maquinas_path = os.path.join(CONFIG_DIR, "maquinas.csv")

# =========================
# CSS PERSONALIZADO
# =========================
def load_css():
    css_path = "assets/style_oscuro.css"
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =========================
# SESIÓN
# =========================
if "logueado" not in st.session_state:
    st.session_state.update({"logueado": False, "usuario": "", "rol": "", "menu": None})

# =========================
# LOGIN
# =========================
def login():
    st.title("🛡️ Inicio de Sesión")
    usuario = st.text_input("👤 Usuario")
    clave = st.text_input("🔒 Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if os.path.exists(usuarios_path):
            df = pd.read_csv(usuarios_path)
            row = df[(df.usuario == usuario) & (df.clave.astype(str) == clave)]
            if not row.empty:
                st.session_state.update({"logueado": True, "usuario": usuario, "rol": row.iloc[0]["rol"]})
                st.rerun()
            else:
                st.error("❌ Credenciales inválidas")
        else:
            st.error("Archivo usuarios.csv no encontrado")

if not st.session_state.logueado:
    login()
    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown(f"👤 Usuario: **{st.session_state.usuario}**")
if st.sidebar.button("🚪 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("---")
menu_admin = ["Registrar Cliente", "Registrar Ficha Técnica", "Visualizar Ficha Técnica", "Registrar Orden de Compra", "Seguimiento de Órdenes", "Registrar Orden de Producción", "Órdenes de Producción", "Programar Producción"]
menu_user = ["Visualizar Ficha Técnica"]

opciones = menu_admin if st.session_state.rol == "Administrador" else menu_user
for opcion in opciones:
    if st.sidebar.button(opcion):
        st.session_state.menu = opcion
        st.rerun()

menu = st.session_state.menu
if not menu:
    st.write("⬅️ Selecciona una opción en la barra lateral para continuar.")
    st.stop()

# =========================
# IMPORTAR MÓDULOS
# =========================
from modules.gestion_clientes import gestionar_clientes
from modules.fichas_tecnicas import registrar_ficha, visualizar_ficha
from modules.ordenes_compra import registrar_oc, seguimiento_oc
from modules.ordenes_produccion import registrar_op, visualizar_op
from modules.programacion import programar_produccion

# =========================
# NAVEGACIÓN
# =========================
if menu == "Registrar Cliente":
    gestionar_clientes(clientes_csv_path)
elif menu == "Registrar Ficha Técnica":
    registrar_ficha(clientes_csv_path, fichas_path, IMG_DIR)
elif menu == "Visualizar Ficha Técnica":
    visualizar_ficha(fichas_path, IMG_DIR)
elif menu == "Registrar Orden de Compra":
    registrar_oc(clientes_csv_path, fichas_path, ordenes_path, detalles_path)
elif menu == "Seguimiento de Órdenes":
    seguimiento_oc(ordenes_path, detalles_path)
elif menu == "Registrar Orden de Producción":
    registrar_op(ordenes_path, detalles_path, op_path, detalle_op_path)
elif menu == "Órdenes de Producción":
    visualizar_op(op_path, detalle_op_path, produccion_real_path, ordenes_path)
elif menu == "Programar Producción":
    programar_produccion(op_path, detalle_op_path, programacion_path, maquinas_path)
