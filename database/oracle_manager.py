from datetime import datetime
from config.database import get_oracle_connection

class OracleManager:

    @staticmethod
    def _registrar_bitacora(cursor, usuario, entidad, operacion, ip="127.0.0.1"):
        """Registra la cabecera de auditoría sin triggers[cite: 2]."""
        cursor.execute("SELECT NVL(MAX(IdBitacora), 0) + 1 FROM BITACORA")
        id_bitacora = cursor.fetchone()[0]
        
        fecha_str = datetime.now().strftime("%Y-%m-%d")
        hora_str = datetime.now().strftime("%H:%M:%S")

        sql = """
            INSERT INTO BITACORA (IdBitacora, Usuario, IP, Entidad, Operacion, Fecha, Hora)
            VALUES (:1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), :7)
        """
        cursor.execute(sql, (id_bitacora, usuario, ip, entidad, operacion, fecha_str, hora_str))
        return id_bitacora

    @classmethod
    def insertar_cliente(cls, id_cliente, nombre, telefono, nit, usuario_app):
        """Inserta cliente en Oracle y registra auditoría programática[cite: 2]."""
        conn = get_oracle_connection()
        cursor = conn.cursor()
        try:
            # 1. Insertar el cliente
            cursor.execute(
                "INSERT INTO CLIENTE (IdCliente, Nombre, Telefono, Nit) VALUES (:1, :2, :3, :4)",
                (id_cliente, nombre, telefono, nit)
            )

            # 2. Registrar Bitácora (sin triggers)
            id_bitacora = cls._registrar_bitacora(cursor, usuario_app, 'CLIENTE', 'INSERT')

            # 3. Registrar Detalle de Bitácora
            cursor.execute("SELECT NVL(MAX(IdDetalleBitacora), 0) + 1 FROM DETALLE_BITACORA")
            id_detalle = cursor.fetchone()[0]

            cursor.execute(
                """INSERT INTO DETALLE_BITACORA (IdDetalleBitacora, IdBitacora, NombreCampo, ValorAnterior, ValorActual)
                   VALUES (:1, :2, :3, NULL, :4)""",
                (id_detalle, id_bitacora, 'Nombre', nombre)
            )

            conn.commit()
            return True, "Cliente registrado y auditado con éxito."
        except Exception as e:
            conn.rollback()
            return False, f"Error en Oracle: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def ejecutar_select_dinamico(sql_query):
        """Ejecuta consultas generadas por la IA en lectura sobre Oracle[cite: 1, 2]."""
        conn = get_oracle_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql_query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()
            conn.close()