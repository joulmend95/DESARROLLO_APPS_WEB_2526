"""
Módulo para gestionar la persistencia de datos en diferentes formatos
TXT, JSON y CSV
"""
import json
import csv
import os

# Rutas de los archivos de datos
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
TXT_FILE = os.path.join(DATA_DIR, 'datos.txt')
JSON_FILE = os.path.join(DATA_DIR, 'datos.json')
CSV_FILE = os.path.join(DATA_DIR, 'datos.csv')

# Asegurar que el directorio data existe
os.makedirs(DATA_DIR, exist_ok=True)


# ================================
# PERSISTENCIA EN FORMATO TXT
# ================================

def guardar_txt(productos):
    """
    Guarda los productos en formato TXT usando la función open()
    Formato: ID|Nombre|Cantidad|Precio|Categoria
    """
    try:
        with open(TXT_FILE, 'w', encoding='utf-8') as archivo:
            # Escribir encabezado
            archivo.write("# Inventario de Productos - Formato TXT\n")
            archivo.write("# Formato: ID|Nombre|Cantidad|Precio|Categoria\n")
            archivo.write("#" + "="*60 + "\n")
            
            # Escribir cada producto
            for producto in productos:
                linea = f"{producto.id}|{producto.nombre}|{producto.cantidad}|{producto.precio}|{producto.categoria}\n"
                archivo.write(linea)
        
        return True, "Datos guardados en TXT correctamente"
    except Exception as e:
        return False, f"Error al guardar en TXT: {str(e)}"


def leer_txt():
    """
    Lee los productos desde el archivo TXT usando la función open()
    Retorna una lista de diccionarios con los datos
    """
    productos = []
    try:
        if not os.path.exists(TXT_FILE):
            return []
        
        with open(TXT_FILE, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                # Ignorar líneas de comentario y vacías
                if linea.strip() and not linea.startswith('#'):
                    # Separar los datos por el delimitador |
                    partes = linea.strip().split('|')
                    if len(partes) == 5:
                        producto = {
                            'id': int(partes[0]),
                            'nombre': partes[1],
                            'cantidad': int(partes[2]),
                            'precio': float(partes[3]),
                            'categoria': partes[4]
                        }
                        productos.append(producto)
        
        return productos
    except Exception as e:
        print(f"Error al leer TXT: {str(e)}")
        return []


# ================================
# PERSISTENCIA EN FORMATO JSON
# ================================

def guardar_json(productos):
    """
    Guarda los productos en formato JSON usando la librería json
    Convierte los objetos Producto a diccionarios antes de guardar
    """
    try:
        # Convertir productos a diccionarios
        productos_dict = {
            "metadata": {
                "formato": "JSON",
                "total_productos": len(productos),
                "descripcion": "Inventario de productos en formato JSON"
            },
            "productos": [producto.a_diccionario() for producto in productos]
        }
        
        # Guardar en archivo JSON con indentación para legibilidad
        with open(JSON_FILE, 'w', encoding='utf-8') as archivo:
            json.dump(productos_dict, archivo, indent=4, ensure_ascii=False)
        
        return True, "Datos guardados en JSON correctamente"
    except Exception as e:
        return False, f"Error al guardar en JSON: {str(e)}"


def leer_json():
    """
    Lee los productos desde el archivo JSON usando la librería json
    Retorna una lista de diccionarios con los datos
    """
    try:
        if not os.path.exists(JSON_FILE):
            return []
        
        with open(JSON_FILE, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            
        # Extraer solo la lista de productos
        if 'productos' in datos:
            return datos['productos']
        else:
            # Compatibilidad con formato antiguo
            return datos if isinstance(datos, list) else []
        
    except Exception as e:
        print(f"Error al leer JSON: {str(e)}")
        return []


# ================================
# PERSISTENCIA EN FORMATO CSV
# ================================

def guardar_csv(productos):
    """
    Guarda los productos en formato CSV usando la librería csv
    Implementa escritura de registros con csv.writer
    """
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as archivo:
            # Crear el escritor CSV
            writer = csv.writer(archivo)
            
            # Escribir encabezado
            writer.writerow(['id', 'nombre', 'cantidad', 'precio', 'categoria', 'estado'])
            
            # Escribir cada producto
            for producto in productos:
                writer.writerow([
                    producto.id,
                    producto.nombre,
                    producto.cantidad,
                    producto.precio,
                    producto.categoria,
                    producto.estado()
                ])
        
        return True, "Datos guardados en CSV correctamente"
    except Exception as e:
        return False, f"Error al guardar en CSV: {str(e)}"


def leer_csv():
    """
    Lee los productos desde el archivo CSV usando la librería csv
    Implementa lectura de registros con csv.reader
    Retorna una lista de diccionarios con los datos
    """
    productos = []
    try:
        if not os.path.exists(CSV_FILE):
            return []
        
        with open(CSV_FILE, 'r', encoding='utf-8') as archivo:
            # Crear el lector CSV
            reader = csv.DictReader(archivo)
            
            # Leer cada fila y convertir a diccionario
            for fila in reader:
                producto = {
                    'id': int(fila['id']),
                    'nombre': fila['nombre'],
                    'cantidad': int(fila['cantidad']),
                    'precio': float(fila['precio']),
                    'categoria': fila['categoria'],
                    'estado': fila.get('estado', 'Desconocido')
                }
                productos.append(producto)
        
        return productos
    except Exception as e:
        print(f"Error al leer CSV: {str(e)}")
        return []


# ================================
# FUNCIONES DE SINCRONIZACIÓN
# ================================

def sincronizar_todos_formatos(productos):
    """
    Sincroniza los datos en todos los formatos (TXT, JSON, CSV)
    Recibe una lista de objetos Producto y los guarda en todos los formatos
    """
    resultados = {
        'txt': guardar_txt(productos),
        'json': guardar_json(productos),
        'csv': guardar_csv(productos)
    }
    
    exitos = sum(1 for resultado, _ in resultados.values() if resultado)
    total = len(resultados)
    
    return exitos == total, resultados


def leer_todos_formatos():
    """
    Lee los datos de todos los formatos disponibles
    Retorna un diccionario con los datos de cada formato
    """
    return {
        'txt': leer_txt(),
        'json': leer_json(),
        'csv': leer_csv()
    }


def cargar_desde_archivo(inventario, formato='json'):
    """
    Carga datos desde un archivo específico e inserta en la base de datos
    Útil para importar datos
    """
    from .bd import get_db_connection
    
    if formato == 'txt':
        datos = leer_txt()
    elif formato == 'json':
        datos = leer_json()
    elif formato == 'csv':
        datos = leer_csv()
    else:
        return False, "Formato no soportado"
    
    try:
        # Cargar en la base de datos
        conn = get_db_connection()
        contador = 0
        
        for producto_dict in datos:
            # Verificar si el producto ya existe (por nombre)
            existe = conn.execute(
                'SELECT id FROM productos WHERE nombre = ?',
                (producto_dict['nombre'],)
            ).fetchone()
            
            if not existe:
                conn.execute(
                    'INSERT INTO productos (nombre, cantidad, precio, categoria) VALUES (?, ?, ?, ?)',
                    (producto_dict['nombre'], producto_dict['cantidad'], 
                     producto_dict['precio'], producto_dict['categoria'])
                )
                contador += 1
        
        conn.commit()
        conn.close()
        
        # Recargar el inventario
        inventario.cargar_desde_db()
        
        return True, f"{contador} productos importados desde {formato.upper()}"
    except Exception as e:
        return False, f"Error al cargar desde archivo: {str(e)}"
