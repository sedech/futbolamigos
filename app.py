import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import sqlite3

# Configuración de la página
st.set_page_config(page_title="FutbolAmigos - MVP", layout="wide", page_icon="⚽")
st.write("Cargando la app...")

# Estilo personalizado
st.markdown("""
    <style>
        .title-text {
            font-size: 3em;
            font-weight: 800;
            color: #1f77b4;
        }
        .section-text {
            font-size: 1.2em;
            color: #333333;
        }
        .stButton>button {
            background-color: #1f77b4;
            color: white;
            border-radius: 10px;
            padding: 0.5em 1em;
        }
        .stTextInput>div>input, .stTextArea>div>textarea {
            border-radius: 10px;
            padding: 0.5em;
            background-color: #ffffff;
            border: 1px solid #ccc;
        }
    </style>
""", unsafe_allow_html=True)

# Conexión a la base de datos SQLite
conn = sqlite3.connect("futbolamigos.db", check_same_thread=False)
c = conn.cursor()

# Crear tablas si no existen
c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT UNIQUE,
        password TEXT,
        ubicacion TEXT,
        habilidad TEXT,
        posicion TEXT,
        disponibilidad TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS partidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        lugar TEXT NOT NULL,
        fecha TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS chat_general (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        usuario_nombre TEXT,
        mensaje TEXT,
        timestamp TEXT
    )
''')
conn.commit()

# Estado de sesión
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'user_nombre' not in st.session_state:
    st.session_state['user_nombre'] = None

# Menú lateral
with st.sidebar:
    st.image("futbol-americano.png", width=100)
    selected = option_menu(
        "Menú FutbolAmigos",
        ["Inicio", "Crear Partido", "Buscar Partidos", "Registro", "Login", "Mi Perfil", "Chat General"],
        icons=["house", "plus", "search", "person-plus", "box-arrow-in-right", "info-circle", "chat-left-text"],
        menu_icon="app-indicator",
        default_index=0,
    )

# Función para cerrar sesión
def logout():
    st.session_state['user_id'] = None
    st.session_state['user_nombre'] = None

# Página: Inicio
if selected == "Inicio":
    st.markdown("<div class='title-text'>¡Bienvenido a FutbolAmigos!</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-text'>Organiza partidos, registra tu perfil y encontrá jugadores como vos cerca.</div>", unsafe_allow_html=True)
    st.image("jugadores-de-futbol.png", width=200)
    if st.session_state['user_id']:
        st.success(f"Conectado como: {st.session_state['user_nombre']}")
        if st.button("Cerrar sesión"):
            logout()
            st.experimental_rerun()

# Página: Crear Partido
elif selected == "Crear Partido":
    st.markdown("<div class='title-text'>Crear Partido</div>", unsafe_allow_html=True)
    if st.session_state['user_id']:
        nombre = st.text_input("Nombre del Partido")
        lugar = st.text_input("Lugar")
        fecha = st.date_input("Fecha", min_value=datetime.today())
        hora = st.time_input("Hora", value=datetime.now().time())
        if st.button("Crear Partido"):
            if nombre and lugar:
                fecha_completa = datetime.combine(fecha, hora).strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO partidos (nombre, lugar, fecha) VALUES (?, ?, ?)",
                          (nombre, lugar, fecha_completa))
                conn.commit()
                st.success("✅ Partido creado correctamente.")
            else:
                st.error("⚠️ Completa todos los campos obligatorios.")
    else:
        st.warning("Debes iniciar sesión para crear un partido.")

# Página: Buscar Partidos
elif selected == "Buscar Partidos":
    st.markdown("<div class='title-text'>Buscar Partidos</div>", unsafe_allow_html=True)
    c.execute("SELECT * FROM partidos ORDER BY fecha")
    partidos = c.fetchall()
    if partidos:
        for partido in partidos:
            st.markdown("----")
            st.subheader(partido[1])
            st.write(f"📍 **Lugar:** {partido[2]}")
            st.write(f"📅 **Fecha:** {partido[3]}")
    else:
        st.info("No hay partidos registrados aún.")

# Página: Registro
elif selected == "Registro":
    st.markdown("<div class='title-text'>Registro de Usuario</div>", unsafe_allow_html=True)
    nombre = st.text_input("Nombre completo")
    correo = st.text_input("Correo electrónico")
    password = st.text_input("Contraseña", type="password")
    confirm_password = st.text_input("Confirmar Contraseña", type="password")
    ubicacion = st.text_input("Ubicación")
    habilidad = st.selectbox("Nivel de Habilidad", ["Principiante", "Intermedio", "Avanzado"])
    posicion = st.text_input("Posición Favorita")
    disponibilidad = st.text_area("Disponibilidad (días/horarios)")
    if st.button("Registrarse"):
        if not nombre or not correo or not password:
            st.error("⚠️ El nombre, correo y contraseña son obligatorios.")
        elif password != confirm_password:
            st.error("⚠️ Las contraseñas no coinciden.")
        else:
            try:
                c.execute("""
                    INSERT INTO usuarios (nombre, correo, password, ubicacion, habilidad, posicion, disponibilidad)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (nombre, correo, password, ubicacion, habilidad, posicion, disponibilidad))
                conn.commit()
                st.success("✅ Registro exitoso. Ahora podés iniciar sesión.")
            except sqlite3.IntegrityError:
                st.error("❌ Este correo ya está registrado.")

# Página: Login
elif selected == "Login":
    st.markdown("<div class='title-text'>Login de Usuario</div>", unsafe_allow_html=True)
    correo = st.text_input("Correo electrónico", key="login_correo")
    password = st.text_input("Contraseña", type="password", key="login_password")
    if st.button("Iniciar sesión"):
        c.execute("SELECT id, nombre FROM usuarios WHERE correo=? AND password=?", (correo, password))
        result = c.fetchone()
        if result:
            st.session_state['user_id'] = result[0]
            st.session_state['user_nombre'] = result[1]
            st.success(f"Bienvenido, {result[1]}!")
            st.experimental_rerun()
        else:
            st.error("❌ Credenciales incorrectas.")

# Página: Mi Perfil
elif selected == "Mi Perfil":
    st.markdown("<div class='title-text'>Mi Perfil</div>", unsafe_allow_html=True)
    if not st.session_state['user_id']:
        st.error("Primero debes iniciar sesión o registrarte para ver tu perfil.")
    else:
        c.execute("""
            SELECT nombre, correo, ubicacion, habilidad, posicion, disponibilidad 
            FROM usuarios WHERE id=?
        """, (st.session_state['user_id'],))
        usuario = c.fetchone()
        if usuario:
            st.write(f"**👤 Nombre:** {usuario[0]}")
            st.write(f"**📧 Correo:** {usuario[1]}")
            st.write(f"**📍 Ubicación:** {usuario[2]}")
            st.write(f"**⚽ Nivel de Habilidad:** {usuario[3]}")
            st.write(f"**🧍 Posición Favorita:** {usuario[4]}")
            st.write(f"**📆 Disponibilidad:** {usuario[5]}")
        else:
            st.error("No se pudieron cargar los datos del perfil.")
        if st.button("Cerrar sesión"):
            logout()
            st.experimental_rerun()

# Página: Chat General
elif selected == "Chat General":
    st.markdown("<div class='title-text'>💬 Chat General</div>", unsafe_allow_html=True)
    if not st.session_state['user_id']:
        st.warning("Necesitás iniciar sesión para participar del chat.")
    else:
        with st.form("form_chat"):
            mensaje = st.text_area("Escribí tu mensaje:")
            enviado = st.form_submit_button("Enviar")
            if enviado and mensaje.strip():
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO chat_general (usuario_id, usuario_nombre, mensaje, timestamp) VALUES (?, ?, ?, ?)",
                          (st.session_state['user_id'], st.session_state['user_nombre'], mensaje, timestamp))
                conn.commit()
                st.success("Mensaje enviado.")
                st.experimental_rerun()

    # Mostrar historial
    c.execute("SELECT usuario_nombre, mensaje, timestamp FROM chat_general ORDER BY timestamp DESC LIMIT 50")
    mensajes = c.fetchall()
    st.markdown("### Mensajes recientes:")
    for nombre, texto, hora in reversed(mensajes):
        st.markdown(f"**{nombre}** ({hora}): {texto}")
