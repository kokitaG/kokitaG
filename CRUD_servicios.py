import pyodbc
import os
from conection_bd import conectar_bd  # Asegúrate de que este archivo existe y funciona



def agregar_servicio_bd(usuario_id, nombre, precio):
    """
    Agrega un nuevo servicio a la base de datos usando el procedimiento almacenado sp_registrar_servicio.
    Args:
        usuario_id (int): ID del usuario que realiza la operación.
        nombre (str): Nombre del servicio.
        precio (float): Precio del servicio.
    Returns:
        bool: True si el servicio se agregó con éxito, False en caso de error.
    """
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            print("Llamando al procedimiento almacenado sp_registrar_servicio...")
            cursor.execute("{CALL sp_registrar_servicio(?, ?, ?)}", (usuario_id, nombre, precio))
            conexion.commit()  # Confirma la transacción
            print("Servicio agregado con éxito (a través de SP).")
            return True
        except pyodbc.Error as e:
            # Captura errores específicos de la base de datos
            print(f"\nError al agregar servicio: {e}")
            if conexion:
                conexion.rollback()  # Revierte la transacción en caso de error
            return False
        finally:
            if conexion:
                conexion.close()
                print("Conexión cerrada.")
    return False


def editar_servicio_bd(usuario_id, servicio_id, nuevo_nombre, nuevo_precio):
    """
    Edita un servicio existente en la base de datos usando el procedimiento almacenado sp_editar_servicio.
    Args:
        usuario_id (int): ID del usuario que realiza la operación.
        servicio_id (int): ID del servicio a editar.
        nuevo_nombre (str): Nuevo nombre del servicio.
        nuevo_precio (float): Nuevo precio del servicio.
    Returns:
        bool: True si el servicio se editó con éxito, False en caso de error.
    """
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            print("Llamando al procedimiento almacenado sp_editar_servicio...")
            cursor.execute("{CALL sp_editar_servicio(?, ?, ?, ?)}",
                           (usuario_id, servicio_id, nuevo_nombre, nuevo_precio))
            conexion.commit()
            if cursor.rowcount > 0:
                print("Servicio editado con éxito (a través de SP).")
                return True
            else:
                print("No se encontró el servicio con el ID proporcionado.")
                return False
        except pyodbc.Error as e:
            print(f"\nError al editar servicio: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()
                print("Conexión cerrada.")
    return False


def eliminar_servicio_bd(usuario_id, servicio_id):
    """
    Elimina un servicio de la base de datos usando el procedimiento almacenado sp_eliminar_servicio.
    Args:
        usuario_id (int): ID del usuario que realiza la operación.
        servicio_id (int): ID del servicio a eliminar.
    Returns:
        bool: True si el servicio se eliminó con éxito, False en caso de error.
    """
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            print("Llamando al procedimiento almacenado sp_eliminar_servicio...")
            cursor.execute("{CALL sp_eliminar_servicio(?, ?)}", (usuario_id, servicio_id))
            conexion.commit()
            if cursor.rowcount > 0:
                print("Servicio eliminado con éxito (a través de SP).")
                return True
            else:
                print("No se encontró el servicio con el ID proporcionado.")
                return False
        except pyodbc.Error as e:
            print(f"\nError al eliminar servicio: {e}")
            if conexion:
                conexion.rollback()
            return False
        finally:
            if conexion:
                conexion.close()
                print("Conexión cerrada.")
    return False



def obtener_todos_servicios_bd():
    """
    Obtiene todos los servicios de la base de datos.
    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa un servicio.
              Retorna una lista vacía en caso de error o si no hay servicios.
    """
    conexion = conectar_bd()
    servicios = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id, nombre, precio FROM dbo.servicios")  # Especifica el esquema dbo
            columnas = [column[0] for column in cursor.description]
            servicios = [dict(zip(columnas, row)) for row in cursor.fetchall()]
            print(f"Se encontraron {len(servicios)} servicios en la BD.")
        except pyodbc.Error as e:
            print(f"\nError al obtener servicios: {e}")
            servicios = []  # Asegura que se retorne una lista vacía en caso de error
        finally:
            if conexion:
                conexion.close()
    return servicios



# ========== FUNCIONES DE LA APLICACIÓN (Interfaz de usuario para el administrador) ==========

def agregar_servicio(usuario_id):
    """
    Permite al administrador agregar un nuevo servicio.
    Args:
        usuario_id (int): ID del usuario que realiza la operación.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Agregar Nuevo Servicio ---")
    nombre = input("Nombre del servicio: ")
    try:
        precio = float(input("Precio del servicio: "))
    except ValueError:
        print("\nError: El precio debe ser un número válido.")
        input("Presione Enter para continuar...")
        return

    # Bypass de la verificación de rol
    if agregar_servicio_bd(1, nombre, precio): # Hardcodeamos el usuario_id a 1 (o el ID del admin)
        print("\nServicio agregado con éxito!")
    else:
        print("\nError al agregar servicio.")
    input("Presione Enter para continuar...")



def editar_servicio(usuario_id):
    """
    Permite al administrador editar un servicio existente.
    Args:
        usuario_id (int): ID del usuario que realiza la operación.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Editar Servicio ---")
    try:
        servicio_id = int(input("Ingrese el ID del servicio a editar: "))
    except ValueError:
        print("\nError: El ID debe ser un número entero válido.")
        input("Presione Enter para continuar...")
        return

    servicios = obtener_todos_servicios_bd() # Obtener la lista de servicios
    servicio_a_editar = None
    for servicio in servicios:
        if servicio['id'] == servicio_id:
            servicio_a_editar = servicio
            break

    if not servicio_a_editar:
        print("\nNo se encontró ningún servicio con ese ID.")
        input("Presione Enter para continuar...")
        return

    print("\n--- Servicio a Editar ---")
    print(f"ID: {servicio_a_editar['id']}")
    print(f"Nombre actual: {servicio_a_editar['nombre']}")
    print(f"Precio actual: {servicio_a_editar['precio']:.2f}")

    nuevo_nombre = input("Nuevo nombre (dejar en blanco para no cambiar): ")
    if not nuevo_nombre:
        nuevo_nombre = servicio_a_editar['nombre']

    nuevo_precio_str = input("Nuevo precio (dejar en blanco para no cambiar): ")
    if nuevo_precio_str:
        try:
            nuevo_precio = float(nuevo_precio_str)
        except ValueError:
            print("Error: El precio debe ser un número válido. Se mantendrá el precio anterior.")
            nuevo_precio = servicio_a_editar['precio']
    else:
        nuevo_precio = servicio_a_editar['precio']

    if editar_servicio_bd(1, servicio_id, nuevo_nombre, nuevo_precio): # Hardcodeamos el usuario_id a 1
        print("\nServicio editado con éxito!")
    else:
        print("\nError al editar servicio.")
    input("Presione Enter para continuar...")



def eliminar_servicio(usuario_id):
    """
    Permite al administrador eliminar un servicio.
    Args:
        usuario_id (int): ID del usuario que realiza la operación.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Eliminar Servicio ---")
    try:
        servicio_id = int(input("Ingrese el ID del servicio a eliminar: "))
    except ValueError:
        print("\nError: El ID debe ser un número entero.")
        input("Presione Enter para continuar...")
        return

    if eliminar_servicio_bd(1, servicio_id): # Hardcodeamos el usuario_id a 1
        print("\nServicio eliminado con éxito!")
    else:
        print("\nError al eliminar servicio.")
    input("Presione Enter para continuar...")

def mostrar_todos_servicios():
    """Muestra una lista de todos los servicios."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Listado de Servicios ---")
    servicios = obtener_todos_servicios_bd()
    if not servicios:
        print("No hay servicios registrados.")
    else:
        for servicio in servicios:
            print(f"\nID: {servicio['id']}")
            print(f"Nombre: {servicio['nombre']}")
            print(f"Precio: ${servicio['precio']:.2f}")
            print("-" * 40)
    input("\nPresione Enter para continuar...")





# ========== FUNCIONES DEL MENÚ ==========

def mostrar_menu_admin_servicios():
    """Muestra el menú de opciones para el administrador de servicios."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Menú Administrador de Servicios ---")
    print("1. Agregar servicio")
    print("2. Mostrar todos los servicios")
    print("3. Actualizar servicio")
    print("4. Eliminar servicio")
    print("5. Volver al menú principal")



def menu_administrador_servicios(usuario_id):
    """
    Función principal para el menú de administración de servicios.
    Args:
        usuario_id: El ID del usuario administrador que ha iniciado sesión.
    """
    while True:
        mostrar_menu_admin_servicios()
        opcion = input("\nSeleccione una opción: ")

        if opcion == '1':
            agregar_servicio(usuario_id)
        elif opcion == '2':
            mostrar_todos_servicios()
        elif opcion == '3':
            editar_servicio(usuario_id)
        elif opcion == '4':
            eliminar_servicio(usuario_id)
        elif opcion == '5':
            break
        else:
            print("\nOpción no válida. Intente nuevamente.")
            input("Presione Enter para continuar...")



# ========== PRUEBA DEL MÓDULO (Ejemplo de uso) ==========
if __name__ == "__main__":
    # Suponemos que ya tienes una forma de obtener el usuario_id del administrador que ha iniciado sesión.
    # Aquí, lo hardcodeamos para simplificar la prueba. ¡NO HAGAS ESTO EN PRODUCCIÓN!
    usuario_id_admin = 1  # <--- ¡CAMBIAR ESTO POR EL ID REAL DEL USUARIO ADMINISTRADOR!

    menu_administrador_servicios(usuario_id_admin)

