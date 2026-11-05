import os
import pyodbc
import oracledb
from dotenv import load_dotenv

load_dotenv()

def get_sqlserver_connection():
    """Conexión directa a SQL Server Express usando Windows Authentication."""
    drivers_instalados = pyodbc.drivers()
    driver_seleccionado = "ODBC Driver 18 for SQL Server" if "ODBC Driver 18 for SQL Server" in drivers_instalados else (
        "ODBC Driver 17 for SQL Server" if "ODBC Driver 17 for SQL Server" in drivers_instalados else "SQL Server"
    )
    
    server_name = os.getenv('SQL_SERVER', r'JULISSA\SQLEXPRESS')
    db_name = os.getenv('SQL_DB', 'MantVehDB')

    conn_str = (
        f"DRIVER={{{driver_seleccionado}}};"
        f"SERVER={server_name};"
        f"DATABASE={db_name};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def get_oracle_connection():
    """Conexión a Oracle Free para lógica de negocio y auditoría."""
    return oracledb.connect(
        user=os.getenv('ORACLE_USER', 'system'),
        password=os.getenv('ORACLE_PASS', 'Julissa'),
        dsn=os.getenv('ORACLE_DSN', 'localhost:1521/FREEPDB1')
    )