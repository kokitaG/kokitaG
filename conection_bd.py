import pyodbc
import os

# Parámetros de conexión

def conectar_bd():
    try:
        con_str_param = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=GONVILLA\\OSCAR1;"
            "DATABASE=hotel_reservaciones;"
            "Trusted_Connection=yes;"
        )
        
        conexion = pyodbc.connect(con_str_param) 
        print("\nConexión a la base de datos establecida con éxito.") # Confirmación visual
        return conexion
    except Exception as e:
        print(f"\nError al conectar a la base de datos: {e}")
        input("Presione Enter para continuar...")
        return None