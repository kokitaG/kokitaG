import pyodbc
import os
from conection_bd import conectar_bd 

# ========== CRUD habitaciones_BD ==========

def agregar_habitacion_bd(habitacion):
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            print("Preparando para insertar habitación...")
                        
            balcon_db = 1 if habitacion['balcon'] else 0
            disponible_db = 1 if habitacion['disponible'] else 0

            # Imprimir los valores que se van a insertar para depuración
            print(f"Valores a insertar: ID={habitacion['id']}, Descripcion={habitacion['descripcion']}, Camas={habitacion['camas']}, Baños={habitacion['banos']}, Vista={habitacion['vista']}, Balcon_DB={balcon_db}, Precio={habitacion['precio']}, Disponible_DB={disponible_db}, Lugar_Turistico={habitacion['lugar_turistico']}")
            
            sql_insert = """
                INSERT INTO dbohabitaciones 
                (id, descripcion, camas, banos, vista, balcon, precio, disponible, Lugar_Turistico)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql_insert, (
                habitacion['id'],
                habitacion['descripcion'],
                habitacion['camas'],
                habitacion['banos'],
                habitacion['vista'],
                balcon_db,
                habitacion['precio'],
                disponible_db,
                habitacion['lugar_turistico'] # ¡Nuevo campo aquí!
            ))
            
            # Verificar si se afectaron filas (si la inserción fue exitosa)
            if cursor.rowcount > 0:
                conexion.commit()
                print("Conexión: Commit realizado con éxito.")
                return True
            else:
                
                print("Advertencia: No se insertaron filas. ¿ID duplicado?")
                conexion.rollback() 
                return False

        except pyodbc.IntegrityError as e:
            # Capturar errores de integridad (ej. ID duplicado)
            print(f"\nError de integridad al agregar habitación (posible ID duplicado): {e}")
            if conexion:
                conexion.rollback() 
            return False
        except Exception as e:
            print(f"\nError general al agregar habitación: {e}")
            if conexion:
                conexion.rollback() # Revertir la transacción si hay error
            return False
        finally:
            if conexion:
                conexion.close()
                print("Conexión: Cerrada.")
    return False

def obtener_todas_habitaciones():
    conexion = conectar_bd()
    habitaciones = []
    if conexion:
        try:
            cursor = conexion.cursor()
            print("Ejecutando SELECT * FROM dbohabitaciones...")
            cursor.execute("SELECT * FROM dbohabitaciones")
            columnas = [column[0] for column in cursor.description]
            habitaciones = [dict(zip(columnas, row)) for row in cursor.fetchall()]
            print(f"Se encontraron {len(habitaciones)} habitaciones en la BD.")
        except Exception as e:
            print(f"\nError al obtener habitaciones: {e}")
            habitaciones = []
        finally:
            if conexion:
                conexion.close()
    return habitaciones

def obtener_habitaciones_disponibles():
    conexion = conectar_bd()
    habitaciones = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM dbohabitaciones WHERE disponible = 1")
            columnas = [column[0] for column in cursor.description]
            habitaciones = [dict(zip(columnas, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"\nError al obtener habitaciones disponibles: {e}")
            habitaciones = []
        finally:
            if conexion:
                conexion.close()
    return habitaciones

def buscar_habitacion_por_id_bd(id_habitacion):
    conexion = conectar_bd()
    habitacion = None
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM dbohabitaciones WHERE id = ?", (id_habitacion,))
            columnas = [column[0] for column in cursor.description]
            result = cursor.fetchone()
            if result:
                habitacion = dict(zip(columnas, result))
        except Exception as e:
            print(f"\nError al buscar habitación: {e}")
            habitacion = None
        finally:
            if conexion:
                conexion.close()
    return habitacion

def actualizar_habitacion_bd(habitacion):
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            # Conversión de True/False a 1/0 para campos BIT al actualizar
            balcon_db = 1 if habitacion['balcon'] else 0
            disponible_db = 1 if habitacion['disponible'] else 0

            cursor.execute("""
                UPDATE dbohabitaciones 
                SET descripcion = ?, camas = ?, banos = ?, vista = ?, 
                    balcon = ?, precio = ?, disponible = ?, Lugar_Turistico = ?
                WHERE id = ?
            """, (
                habitacion['descripcion'],
                habitacion['camas'],
                habitacion['banos'],
                habitacion['vista'],
                balcon_db,       # Usamos el valor convertido
                habitacion['precio'],
                disponible_db,   # Usamos el valor convertido
                habitacion['lugar_turistico'], # ¡Nuevo campo aquí!
                habitacion['id']
            ))
            conexion.commit()
            return True
        except Exception as e:
            print(f"\nError al actualizar habitación: {e}")
            return False
        finally:
            if conexion:
                conexion.close()
    return False

def eliminar_habitacion_bd(id_habitacion):
    conexion = conectar_bd()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM dbohabitaciones WHERE id = ?", (id_habitacion,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"\nError al eliminar habitación: {e}")
            return False
        finally:
            if conexion:
                conexion.close()
    return False

# ========== FUNCIONES DE LA APLICACIÓN ==========

def agregar_habitacion():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Agregar Nueva Habitación ---")
    id_habitacion = input("ID de la habitación: ")
    
    if buscar_habitacion_por_id_bd(id_habitacion):
        print("\nError: Ya existe una habitación con ese ID.")
        input("Presione Enter para continuar...")
        return
    
    descripcion = input("Descripción: ")
    camas = int(input("Número de camas: "))
    banos = int(input("Número de baños: "))
    vista = input("Vista (mar/montaña/ciudad): ")
    tiene_balcon = input("¿Tiene balcón? (si/no): ").lower() == 'si'
    precio = float(input("Precio por noche: "))
    disponible = input("¿Disponible? (si/no): ").lower() == 'si'
    lugar_turistico = input("Lugar turístico cercano: ") # ¡Nuevo input aquí!
    
    nueva_habitacion = {
        'id': id_habitacion,
        'descripcion': descripcion,
        'camas': camas,
        'banos': banos,
        'vista': vista,
        'balcon': tiene_balcon,
        'precio': precio,
        'disponible': disponible,
        'lugar_turistico': lugar_turistico # ¡Nuevo campo en el diccionario!
    }
    
    if agregar_habitacion_bd(nueva_habitacion):
        print("\nHabitación agregada con éxito!")
    else:
        print("\nError al agregar habitación.")
    input("Presione Enter para continuar...")

def mostrar_todas_habitaciones():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Listado de Habitaciones ---")
    habitaciones = obtener_todas_habitaciones() # Ahora con mensaje de cuántas encontró
    
    if not habitaciones:
        print("No hay habitaciones registradas.")
    else:
        for hab in habitaciones:
            # Asegúrate de que los campos BIT se muestren correctamente (True/False o Sí/No)
            balcon_display = 'Sí' if hab.get('balcon') else 'No' # .get() para evitar KeyError si la columna falta
            disponible_display = 'Sí' if hab.get('disponible') else 'No'

            print(f"\nID: {hab.get('id')}")
            print(f"Descripción: {hab.get('descripcion')}")
            print(f"Camas: {hab.get('camas')} - Baños: {hab.get('banos')}")
            print(f"Vista: {hab.get('vista')} - Balcón: {balcon_display}")
            print(f"Precio: ${hab.get('precio', 0.0):.2f} por noche") # .get() con valor por defecto
            print(f"Disponible: {disponible_display}")
            print(f"Lugar Turístico: {hab.get('Lugar_Turistico', 'N/A')}") # ¡Nuevo campo aquí!
            print("-" * 40)
    
    input("\nPresione Enter para continuar...")

def buscar_habitacion_por_id():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Buscar Habitación por ID ---")
    id_buscar = input("Ingrese el ID de la habitación: ")
    
    habitacion = buscar_habitacion_por_id_bd(id_buscar)
    
    if habitacion:
        balcon_display = 'Sí' if habitacion.get('balcon') else 'No'
        disponible_display = 'Sí' if habitacion.get('disponible') else 'No'

        print("\n--- Habitación Encontrada ---")
        print(f"ID: {habitacion.get('id')}")
        print(f"Descripción: {habitacion.get('descripcion')}")
        print(f"Camas: {habitacion.get('camas')} - Baños: {habitacion.get('banos')}")
        print(f"Vista: {habitacion.get('vista')} - Balcón: {balcon_display}")
        print(f"Precio: ${habitacion.get('precio', 0.0):.2f} por noche")
        print(f"Disponible: {disponible_display}")
        print(f"Lugar Turístico: {habitacion.get('Lugar_Turistico', 'N/A')}") # ¡Nuevo campo aquí!
        
        if not habitacion.get('disponible'):
            print("\nEsta habitación no está disponible actualmente.")
    else:
        print("\nNo se encontró ninguna habitación con ese ID.")
    
    input("\nPresione Enter para continuar...")

def actualizar_habitacion():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Actualizar Habitación ---")
    id_actualizar = input("Ingrese el ID de la habitación a actualizar: ")
    
    habitacion = buscar_habitacion_por_id_bd(id_actualizar)
    
    if not habitacion:
        print("\nNo se encontró ninguna habitación con ese ID.")
        input("Presione Enter para continuar...")
        return
    
    print("\nDeje en blanco los campos que no desea modificar.")
    
    descripcion = input(f"Nueva descripción [{habitacion['descripcion']}]: ")
    if descripcion:
        habitacion['descripcion'] = descripcion
        
    camas = input(f"Nuevo número de camas [{habitacion['camas']}]: ")
    if camas:
        try:
            habitacion['camas'] = int(camas)
        except ValueError:
            print("Valor inválido para camas. Se mantendrá el valor anterior.")
            
    banos = input(f"Nuevo número de baños [{habitacion['banos']}]: ")
    if banos:
        try:
            habitacion['banos'] = int(banos)
        except ValueError:
            print("Valor inválido para baños. Se mantendrá el valor anterior.")
        
    vista = input(f"Nueva vista [{habitacion['vista']}]: ")
    if vista:
        habitacion['vista'] = vista
        
    balcon_actual_str = 'si' if habitacion['balcon'] else 'no'
    balcon = input(f"¿Tiene balcón? [{balcon_actual_str}]: ").lower()
    if balcon in ['si', 'no']: # Validar entrada
        habitacion['balcon'] = balcon == 'si'
    elif balcon: # Si se ingresó algo pero no es 'si' o 'no'
        print("Valor inválido para balcón. Se mantendrá el valor anterior.")
        
    precio = input(f"Nuevo precio [{habitacion['precio']}]: ")
    if precio:
        try:
            habitacion['precio'] = float(precio)
        except ValueError:
            print("Valor inválido para precio. Se mantendrá el valor anterior.")
        
    disponible_actual_str = 'si' if habitacion['disponible'] else 'no'
    disponible = input(f"¿Disponible? [{disponible_actual_str}]: ").lower()
    if disponible in ['si', 'no']: # Validar entrada
        habitacion['disponible'] = disponible == 'si'
    elif disponible: # Si se ingresó algo pero no es 'si' o 'no'
        print("Valor inválido para disponible. Se mantendrá el valor anterior.")

    lugar_turistico = input(f"Nuevo Lugar Turístico [{habitacion.get('Lugar_Turistico', 'N/A')}]: ") # ¡Nuevo input aquí!
    if lugar_turistico:
        habitacion['lugar_turistico'] = lugar_turistico
        
    if actualizar_habitacion_bd(habitacion):
        print("\nHabitación actualizada con éxito!")
    else:
        print("\nError al actualizar habitación.")
    input("Presione Enter para continuar...")

def eliminar_habitacion():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Eliminar Habitación ---")
    id_eliminar = input("Ingrese el ID de la habitación a eliminar: ")
    
    if eliminar_habitacion_bd(id_eliminar):
        print("\nHabitación eliminada con éxito!")
    else:
        print("\nNo se encontró ninguna habitación con ese ID o ocurrió un error.")
    input("Presione Enter para continuar...")

def mostrar_habitaciones_disponibles():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Habitaciones Disponibles ---")
    habitaciones = obtener_habitaciones_disponibles()
    
    if not habitaciones:
        print("No hay habitaciones disponibles en este momento.")
    else:
        for hab in habitaciones:
            balcon_display = 'Sí' if hab.get('balcon') else 'No'
            disponible_display = 'Sí' if hab.get('disponible') else 'No'

            print(f"\nID: {hab.get('id')}")
            print(f"Descripción: {hab.get('descripcion')}")
            print(f"Camas: {hab.get('camas')} - Baños: {hab.get('banos')}")
            print(f"Vista: {hab.get('vista')} - Balcón: {balcon_display}")
            print(f"Precio: ${hab.get('precio', 0.0):.2f} por noche")
            print(f"Lugar Turístico: {hab.get('Lugar_Turistico', 'N/A')}") # ¡Nuevo campo aquí!
            print("-" * 40)
    
    input("\nPresione Enter para continuar...")

def buscar_habitacion_cliente():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Buscar Habitación ---")
    id_buscar = input("Ingrese el ID de la habitación: ")
    
    habitacion = buscar_habitacion_por_id_bd(id_buscar)
    
    if habitacion:
        balcon_display = 'Sí' if habitacion.get('balcon') else 'No'
        disponible_display = 'Sí' if habitacion.get('disponible') else 'No'

        print("\n--- Habitación Encontrada ---")
        print(f"ID: {habitacion.get('id')}")
        print(f"Descripción: {habitacion.get('descripcion')}")
        print(f"Camas: {habitacion.get('camas')} - Baños: {habitacion.get('banos')}")
        print(f"Vista: {habitacion.get('vista')} - Balcón: {balcon_display}")
        print(f"Precio: ${habitacion.get('precio', 0.0):.2f} por noche")
        print(f"Disponible: {disponible_display}")
        print(f"Lugar Turístico: {habitacion.get('Lugar_Turistico', 'N/A')}") # ¡Nuevo campo aquí!
        
        if not habitacion.get('disponible'):
            print("\nEsta habitación no está disponible actualmente.")
    else:
        print("\nNo se encontró ninguna habitación con ese ID.")
    
    input("\nPresione Enter para continuar...")

# ========== FUNCIONES DEL MENÚ ==========

def mostrar_menu_principal():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Sistema de Gestión de Habitaciones ---")
    print("1. Ingresar como Administrador")
    print("2. Ingresar como Cliente")
    print("3. Salir")

def mostrar_menu_admin():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Menú Administrador ---")
    print("1. Agregar habitación")
    print("2. Mostrar todas las habitaciones")
    print("3. Buscar habitación por ID")
    print("4. Actualizar habitación")
    print("5. Eliminar habitación")
    print("6. Volver al menú principal")

def mostrar_menu_cliente():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n--- Menú Cliente ---")
    print("1. Ver habitaciones disponibles")
    print("2. Buscar habitación por ID")
    print("3. Volver al menú principal")

def menu_administrador():
    while True:
        mostrar_menu_admin()
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            agregar_habitacion()
        elif opcion == '2':
            mostrar_todas_habitaciones()
        elif opcion == '3':
            buscar_habitacion_por_id()
        elif opcion == '4':
            actualizar_habitacion()
        elif opcion == '5':
            eliminar_habitacion()
        elif opcion == '6':
            break
        else:
            print("\nOpción no válida. Intente nuevamente.")
            input("Presione Enter para continuar...")

def menu_cliente():
    while True:
        mostrar_menu_cliente()
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            mostrar_habitaciones_disponibles()
        elif opcion == '2':
            buscar_habitacion_cliente()
        elif opcion == '3':
            break
        else:
            print("\nOpción no válida. Intente nuevamente.")
            input("Presione Enter para continuar...")

# ========== FUNCIÓN PRINCIPAL ==========

def main():
        
    while True:
        mostrar_menu_principal()
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            menu_administrador()
        elif opcion == '2':
            menu_cliente()
        elif opcion == '3':
            print("\nSaliendo del sistema...")
            break
        else:
            print("\nOpción no válida. Intente nuevamente.")
            input("Presione Enter para continuar...")

if __name__ == "__main__":
    main()