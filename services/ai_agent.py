import os
import openai

ESQUEMA_ORACLE = """
Tablas disponibles en Oracle:
- CLIENTE(IdCliente, Nombre, Telefono, Nit)
- VEHICULO(IdVehiculo, Placa, Marca, TipoVehiculo, Modelo, Anio, IdCliente)
- ORDEN_TRABAJO(IdOrden, IdVehiculo, FechaRecepcion, FechaEntrega, Estado, FormaPago)
- FACTURA(IdFactura, IdOrden, Fecha, Total)
- MECANICO(IdMecanico, Nombre, Especialidad)
- REPUESTO(IdRepuesto, Nombre, Precio, Existencia)
"""

class AIAgentService:
    def __init__(self, api_key=None):
        key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=key)

    def responder_o_generar_sql(self, prompt_usuario):
        prompt = f"""
        Eres un asistente experto para el módulo de Mantenimiento de Vehículos.
        Esquema de la base de datos Oracle:
        {ESQUEMA_ORACLE}

        Si el usuario te hace una pregunta sobre los datos, genera ÚNICAMENTE la sentencia SQL SELECT de Oracle correspondiente.
        No incluyas markdown, saltos de línea adicionales ni la palabra 'sql'. Solo la sentencia pura.

        Consulta del usuario: {prompt_usuario}
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        sql = response.choices[0].message.content.strip()
        return sql.replace("```sql", "").replace("```", "").strip()