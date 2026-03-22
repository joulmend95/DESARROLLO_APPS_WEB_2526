import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

def get_db_connection():
    """
    Establece la conexión con la base de datos MySQL local o remota.
    Extrae las credenciales de forma segura desde el archivo .env
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        if connection.is_connected():
            print("Conexión exitosa a la base de datos MySQL")
            return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def close_db_connection(connection):
    """
    Cierra la conexión con la base de datos de manera segura.
    """
    if connection and connection.is_connected():
        connection.close()
        print("Conexión a MySQL cerrada correctamente")
