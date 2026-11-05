import streamlit as st
import pandas as pd
from datetime import datetime
from database.sqlserver_manager import SQLServerManager

# Configuración de página
st.set_page_config(page_title="Sistema MantVeh - Prototipo IA", page_icon="🚗", layout="wide")

# Estilos CSS personalizados
st.markdown("""
<style>
    .main { background-color: #0F172A; }
    
    /* Indicadores KPI */
    [data-testid="stMetricValue"] {
        font-size: 30px !important;
        color: #FF6B00 !important;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 13px !important;
    }
    
    /* Cajas y formularios */
    div[data-testid="stExpander"], div[data-testid="stForm"] {
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        background-color: #1E293B;
    }
    
    .stButton>button[kind="primary"] {
        background-color: #FF6B00 !important;
        border: none;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Estado Global de la Aplicación
if "usuario_autenticado" not in st.session_state:
    st.session_state["usuario_autenticado"] = None

if "tickets_db" not in st.session_state:
    st.session_state["tickets_db"] = [
        {"id": "TCK-1001", "vehiculo": "P-123ABC", "mecanico": "Carlos López", "tipo": "Preventivo", "prioridad": "Alta", "estado": "En Proceso", "fecha": "2026-11-01"},
        {"id": "TCK-1002", "vehiculo": "P-456DEF", "mecanico": "Ana Martínez", "tipo": "Correctivo", "prioridad": "Crítica", "estado": "Abierto", "fecha": "2026-11-03"},
    ]

if "mecanicos_db" not in st.session_state:
    st.session_state["mecanicos_db"] = [
        {"id": 1, "nombre": "Carlos López", "especialidad": "Motor Diésel y Transmisiones", "estado": "Ocupado", "tickets_activos": 1},
        {"id": 2, "nombre": "Ana Martínez", "especialidad": "Sistema Eléctrico y Diagnóstico IA", "estado": "Ocupado", "tickets_activos": 1},
        {"id": 3, "nombre": "Jorge Ramírez", "especialidad": "Frenos y Suspensión", "estado": "Disponible", "tickets_activos": 0},
    ]

if "vehiculos_db" not in st.session_state:
    st.session_state["vehiculos_db"] = [
        {"placa": "P-123ABC", "marca": "Toyota", "modelo": "Hilux 2022", "km": 45000, "estado": "En Taller"},
        {"placa": "P-456DEF", "marca": "Isuzu", "modelo": "NPR 2021", "km": 88000, "estado": "En Taller"},
        {"placa": "P-789GHI", "marca": "Ford", "modelo": "Ranger 2023", "km": 22000, "estado": "Operativo"},
    ]

if "auditoria_db" not in st.session_state:
    st.session_state["auditoria_db"] = [
        {"ID Audit": 501, "Tabla": "ORDENES_TRABAJO", "Acción": "INSERT", "Usuario": "admin", "Fecha": "2026-11-04 10:15", "Detalle": "Ticket TCK-1002 creado en SQL Server"},
        {"ID Audit": 502, "Tabla": "MECANICOS", "Acción": "UPDATE", "Usuario": "admin", "Fecha": "2026-11-04 10:16", "Detalle": "Estado mecánico Carlos López -> Ocupado"},
        {"ID Audit": 503, "Tabla": "VEHICULOS", "Acción": "UPDATE", "Usuario": "system", "Fecha": "2026-11-04 10:20", "Detalle": "Trigger Oracle: Estado P-123ABC actualizado"},
    ]

# ----------------------------------------------------
# 1. AUTENTICACIÓN (SQL SERVER)
# ----------------------------------------------------
if st.session_state["usuario_autenticado"] is None:
    st.markdown("<br><h1 style='text-align: center; color: #FF6B00;'>🚗 Sistema MantVeh</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>Gestión de Mantenimiento Vehicular | SQL Server & Oracle 26ai</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("🔐 Autenticación de Usuario")
            user_in = st.text_input("Usuario", value="admin")
            pass_in = st.text_input("Contraseña", type="password", value="Julissa2026#")
            btn_submit = st.form_submit_button("Ingresar al Sistema", use_container_width=True, type="primary")

            if btn_submit:
                exito, res = SQLServerManager.autenticar_usuario(user_in, pass_in)
                if exito:
                    st.session_state["usuario_autenticado"] = res
                    st.success(f"¡Bienvenido(a), {res['nombre']}!")
                    st.rerun()
                else:
                    st.error(res)

# ----------------------------------------------------
# 2. PANEL PRINCIPAL Y NAVEGACIÓN
# ----------------------------------------------------
else:
    user = st.session_state["usuario_autenticado"]

    with st.sidebar:
        st.markdown("<h2 style='color: #FF6B00;'>🚗 MantVeh System</h2>", unsafe_allow_html=True)
        st.write(f"👤 **Usuario:** `{user['username']}`")
        st.write(f"🛡️ **Perfil:** `{user['perfil']}`")
        st.write(f"📌 **Nombre:** {user['nombre']}")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state["usuario_autenticado"] = None
            st.rerun()

        st.divider()
        st.subheader("📋 Menú de Opciones (SQL Server)")
        menus = SQLServerManager.obtener_menus_usuario(user["id_perfil"])
        
        opciones_menu = {m["NombreMenu"]: m["Ruta"] for m in menus}
        seleccion = st.radio("Navegación:", list(opciones_menu.keys()))
        ruta_actual = opciones_menu[seleccion]

    # --- MÓDULOS DE SISTEMA ---

    # A. DASHBOARD EJECUTIVO (Sin Gráficas)
    if ruta_actual == "dashboard":
        st.title("📊 Resumen Operativo de la Flota")
        st.caption("Panel de control gerencial con alertas y métricas en tiempo real.")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Vehículos", len(st.session_state["vehiculos_db"]), "Unidades en Flota")
        
        en_taller = sum(1 for v in st.session_state["vehiculos_db"] if v["estado"] == "En Taller")
        k2.metric("Unidades en Taller", en_taller, "Requieren Atención")
        
        activos = sum(1 for t in st.session_state["tickets_db"] if t["estado"] != "Completado")
        k3.metric("Tickets Abiertos", activos, "En Proceso / Pendientes")
        
        k4.metric("Registros Auditoría", len(st.session_state["auditoria_db"]), "Triggers Oracle")

        st.divider()

        # Secciones Informativas
        col_sec1, col_sec2 = st.columns(2)

        with col_sec1:
            st.subheader("⚠️ Alertas de Mantenimiento Prioritario")
            for t in st.session_state["tickets_db"]:
                if t["prioridad"] in ["Alta", "Crítica"] and t["estado"] != "Completado":
                    st.warning(f"**{t['id']}** | Vehículo: `{t['vehiculo']}` | Mecánico: {t['mecanico']} | Prioridad: **{t['prioridad']}**")

        with col_sec2:
            st.subheader("👨‍🔧 Disponibilidad del Personal Técnico")
            df_m = pd.DataFrame(st.session_state["mecanicos_db"])[["nombre", "especialidad", "estado", "tickets_activos"]]
            st.dataframe(df_m, use_container_width=True)

        st.subheader("📋 Resumen General de Órdenes de Trabajo")
        st.dataframe(pd.DataFrame(st.session_state["tickets_db"]), use_container_width=True)

    # B. GESTIÓN DE VEHÍCULOS
    elif ruta_actual == "vehiculos":
        st.title("🚗 Control y Registro de Vehículos")
        
        with st.expander("➕ Registrar Nuevo Vehículo en la Flota"):
            with st.form("form_vehiculo"):
                c1, c2, c3 = st.columns(3)
                placa = c1.text_input("Placa")
                marca = c2.text_input("Marca")
                modelo = c3.text_input("Modelo")
                km = c1.number_input("Kilometraje Acumulado", min_value=0, step=1000)
                estado_v = c2.selectbox("Estado Inicial", ["Operativo", "En Taller", "Mantenimiento"])
                btn_v = st.form_submit_button("Guardar Vehículo", type="primary")

                if btn_v and placa:
                    st.session_state["vehiculos_db"].append({
                        "placa": placa, "marca": marca, "modelo": modelo, "km": km, "estado": estado_v
                    })
                    st.session_state["auditoria_db"].append({
                        "ID Audit": 500 + len(st.session_state["auditoria_db"]) + 1,
                        "Tabla": "VEHICULOS", "Acción": "INSERT", "Usuario": user["username"],
                        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Detalle": f"Ingreso de vehículo {placa}"
                    })
                    st.success(f"Vehículo {placa} ingresado exitosamente.")
                    st.rerun()

        st.subheader("Buscador de Vehículos")
        busqueda_v = st.text_input("🔍 Filtrar por Placa, Marca o Modelo:", "")
        df_v = pd.DataFrame(st.session_state["vehiculos_db"])
        
        if busqueda_v:
            df_v = df_v[df_v.apply(lambda r: busqueda_v.lower() in r.astype(str).str.lower().values, axis=1)]

        st.dataframe(df_v, use_container_width=True)
        
        csv_v = df_v.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte de Vehículos (CSV)", data=csv_v, file_name="reporte_vehiculos.csv", mime="text/csv")

    # C. GESTIÓN DE MECÁNICOS
    elif ruta_actual == "mecanicos":
        st.title("👨‍🔧 Registro de Mecánicos y Asignación")
        
        with st.expander("➕ Registrar Nuevo Mecánico"):
            with st.form("form_mec"):
                c1, c2 = st.columns(2)
                nombre_m = c1.text_input("Nombre Completo")
                esp_m = c2.text_input("Especialidad Técnica")
                btn_m = st.form_submit_button("Guardar Mecánico", type="primary")

                if btn_m and nombre_m:
                    st.session_state["mecanicos_db"].append({
                        "id": len(st.session_state["mecanicos_db"]) + 1,
                        "nombre": nombre_m, "especialidad": esp_m,
                        "estado": "Disponible", "tickets_activos": 0
                    })
                    st.success(f"Mecánico {nombre_m} registrado.")
                    st.rerun()

        st.subheader("Nómina y Carga de Trabajo Técnicos")
        st.dataframe(pd.DataFrame(st.session_state["mecanicos_db"]), use_container_width=True)

    # D. TICKETS Y ÓRDENES DE TRABAJO
    elif ruta_actual == "tickets":
        st.title("🎫 Gestión de Tickets de Trabajo")
        
        col_t1, col_t2 = st.columns([2, 1])
        
        with col_t1:
            with st.expander("📝 Generar Nueva Orden de Trabajo"):
                with st.form("form_ticket"):
                    c1, c2 = st.columns(2)
                    veh_list = [v["placa"] for v in st.session_state["vehiculos_db"]]
                    mec_list = [m["nombre"] for m in st.session_state["mecanicos_db"]]

                    v_sel = c1.selectbox("Vehículo Target", veh_list)
                    m_sel = c2.selectbox("Mecánico Asignado", mec_list)
                    tipo_t = c1.selectbox("Tipo de Mantenimiento", ["Preventivo", "Correctivo", "Diagnóstico IA"])
                    prio_t = c2.selectbox("Prioridad", ["Baja", "Media", "Alta", "Crítica"])
                    btn_t = st.form_submit_button("Crear Ticket", type="primary")

                    if btn_t:
                        tck_id = f"TCK-{1000 + len(st.session_state['tickets_db']) + 1}"
                        st.session_state["tickets_db"].append({
                            "id": tck_id, "vehiculo": v_sel, "mecanico": m_sel,
                            "tipo": tipo_t, "prioridad": prio_t, "estado": "En Proceso",
                            "fecha": datetime.now().strftime("%Y-%m-%d")
                        })
                        for v in st.session_state["vehiculos_db"]:
                            if v["placa"] == v_sel: v["estado"] = "En Taller"
                        for m in st.session_state["mecanicos_db"]:
                            if m["nombre"] == m_sel:
                                m["estado"] = "Ocupado"
                                m["tickets_activos"] += 1

                        st.success(f"Orden {tck_id} creada y asignada.")
                        st.rerun()

        with col_t2:
            st.subheader("🔄 Cambiar Estado Ticket")
            t_ids = [t["id"] for t in st.session_state["tickets_db"] if t["estado"] != "Completado"]
            if t_ids:
                selected_t = st.selectbox("Ticket Pendiente:", t_ids)
                nuevo_est = st.selectbox("Nuevo Estado:", ["En Proceso", "Completado", "Cancelado"])
                
                if st.button("Actualizar Ticket"):
                    for t in st.session_state["tickets_db"]:
                        if t["id"] == selected_t:
                            t["estado"] = nuevo_est
                            if nuevo_est == "Completado":
                                for m in st.session_state["mecanicos_db"]:
                                    if m["nombre"] == t["mecanico"] and m["tickets_activos"] > 0:
                                        m["tickets_activos"] -= 1
                                        if m["tickets_activos"] == 0: m["estado"] = "Disponible"
                                for v in st.session_state["vehiculos_db"]:
                                    if v["placa"] == t["vehiculo"]: v["estado"] = "Operativo"
                            st.success(f"Ticket {selected_t} marcado como {nuevo_est}.")
                            st.rerun()
            else:
                st.info("No hay tickets pendientes por cerrar.")

        st.subheader("Histórico de Ordenes de Trabajo")
        st.dataframe(pd.DataFrame(st.session_state["tickets_db"]), use_container_width=True)

    # E. MANTENIMIENTO PREVENTIVO
    elif ruta_actual == "mantenimiento":
        st.title("🛠️ Plan de Mantenimiento Preventivo")
        st.caption("Matriz de programación según recorrido y tiempo transcurrido.")
        
        plan_df = pd.DataFrame([
            {"Vehículo": "P-123ABC", "Servicio Requerido": "Cambio Aceite Motor 10W40", "Próxima Fecha": "2026-11-15", "Estado": "Próximo"},
            {"Vehículo": "P-456DEF", "Servicio Requerido": "Revisión Sistema de Frenos", "Próxima Fecha": "2026-11-02", "Estado": "Vencido"},
            {"Vehículo": "P-789GHI", "Servicio Requerido": "Alineación y Balanceo", "Próxima Fecha": "2026-12-20", "Estado": "Al Día"},
        ])
        st.table(plan_df)

    # F. ASISTENTE IA (ORACLE 26ai)
    elif ruta_actual == "asistente_ia":
        st.title("🤖 Asistente IA para Diagnósticos & SQL (Oracle 26ai)")
        st.caption("Consulte sobre fallas técnicas o generación de consultas SQL automatizadas.")

        prompt = st.text_input("Ingrese la consulta técnica o síntoma detectado:", "Generar SQL para listar unidades con más de 40,000 km que están en taller")
        
        if st.button("Procesar Consulta IA", type="primary"):
            st.divider()
            st.subheader("💡 Diagnóstico Generado por el Motor IA")
            st.markdown(f"**Consulta evaluada:** *{prompt}*")
            st.markdown("""
            **Resultados del Análisis:**
            1. **Vehículo detectado:** Unit `P-123ABC` (45,000 km, Toyota Hilux).
            2. **Diagnóstico preliminar:** Falla por desgaste regular de fluidos.
            3. **Recomendación:** Generar ticket preventivo y asignar a especialista en motor.
            """)
            
            st.subheader("🔍 Código SQL Generado para Oracle 26ai")
            st.code("""
-- Script automatizado generado por Oracle 26ai
SELECT v.PLACA, v.MARCA, v.MODELO, v.KILOMETRAJE, ot.ESTADO
FROM MANTVEH.VEHICULOS v
INNER JOIN MANTVEH.ORDENES_TRABAJO ot ON v.PLACA = ot.VEHICULO
WHERE v.KILOMETRAJE >= 40000 AND ot.ESTADO = 'En Taller'
ORDER BY v.KILOMETRAJE DESC;
            """, language="sql")

    # G. AUDITORÍA Y TRAZABILIDAD (ORACLE)
    elif ruta_actual == "auditoria":
        st.title("📜 Logs de Auditoría y Triggers (Oracle)")
        st.caption("Registro inalterable de auditoría sobre transacciones de la base de datos.")
        
        if st.button("⚡ Simular Ejecución de Trigger Oracle"):
            st.session_state["auditoria_db"].append({
                "ID Audit": 500 + len(st.session_state["auditoria_db"]) + 1,
                "Tabla": "ORDENES_TRABAJO",
                "Acción": "UPDATE",
                "Usuario": user["username"],
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Detalle": "Trigger TRG_AUDIT_OT invocado correctamente en Oracle"
            })
            st.success("Evento de auditoría registrado por el Trigger.")
            st.rerun()

        st.dataframe(pd.DataFrame(st.session_state["auditoria_db"]), use_container_width=True)