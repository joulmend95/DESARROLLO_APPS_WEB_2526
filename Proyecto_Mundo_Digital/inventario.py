import sqlite3

# Constantes (Tupla)
ESTADOS_PRODUCTO = ("Disponible", "Agotado", "Descontinuado")

def get_db_connection():
    # Conexión a SQLite
    conn = sqlite3.connect('inventario.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Inicializa la base de datos y crea la tabla si no existe
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Programación Orientada a Objetos: Clase Producto
class Producto:
    def __init__(self, id, nombre, cantidad, precio, categoria):
        self._id = id                # Atributo protegido/privado
        self._nombre = nombre
        self._cantidad = cantidad
        self._precio = precio
        self._categoria = categoria

    # Uso de decoradores @property para getters y setters
    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = valor

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor):
        if valor < 0:
            raise ValueError("La cantidad no puede ser negativa")
        self._cantidad = valor

    @property
    def precio(self):
        return self._precio

    @precio.setter
    def precio(self, valor):
        if valor < 0:
            raise ValueError("El precio no puede ser negativo")
        self._precio = valor

    @property
    def categoria(self):
        return self._categoria

    @categoria.setter
    def categoria(self, valor):
        self._categoria = valor

    def estado(self):
        # Uso de tuplas para condiciones
        if self._cantidad > 0:
            return ESTADOS_PRODUCTO[0]
        return ESTADOS_PRODUCTO[1]

    def a_diccionario(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'cantidad': self.cantidad,
            'precio': self.precio,
            'categoria': self.categoria,
            'estado': self.estado()
        }

# Programación Orientada a Objetos: Clase Inventario
class Inventario:
    def __init__(self):
        # Colección: Diccionario para almacenar productos en memoria (Búsqueda rápida por ID)
        self.productos_cache = {}
        # Colección: Conjunto (Set) para almacenar categorías únicas
        self.categorias_unicas = set()
        self.cargar_desde_db()

    def cargar_desde_db(self):
        self.productos_cache.clear()
        self.categorias_unicas.clear()
        conn = get_db_connection()
        rows = conn.execute('SELECT * FROM productos').fetchall()
        for row in rows:
            prod = Producto(row['id'], row['nombre'], row['cantidad'], row['precio'], row['categoria'])
            self.productos_cache[prod.id] = prod
            self.categorias_unicas.add(prod.categoria)
        conn.close()

    def añadir_producto(self, nombre, cantidad, precio, categoria):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO productos (nombre, cantidad, precio, categoria) VALUES (?, ?, ?, ?)',
                    (nombre, cantidad, precio, categoria))
        conn.commit()
        nuevo_id = cur.lastrowid
        conn.close()
        
        # Sincronizar colecciones en memoria
        nuevo_producto = Producto(nuevo_id, nombre, cantidad, precio, categoria)
        self.productos_cache[nuevo_id] = nuevo_producto
        self.categorias_unicas.add(categoria)
        return nuevo_producto

    def eliminar_producto(self, id_producto):
        conn = get_db_connection()
        conn.execute('DELETE FROM productos WHERE id = ?', (id_producto,))
        conn.commit()
        conn.close()
        
        # Sincronizar diccionario en memoria
        if id_producto in self.productos_cache:
            del self.productos_cache[id_producto]
            self._recalcular_categorias()

    def actualizar_producto(self, id_producto, nombre, cantidad, precio, categoria):
        conn = get_db_connection()
        conn.execute('UPDATE productos SET nombre = ?, cantidad = ?, precio = ?, categoria = ? WHERE id = ?',
                     (nombre, cantidad, precio, categoria, id_producto))
        conn.commit()
        conn.close()
        
        # Sincronizar en memoria
        if id_producto in self.productos_cache:
            prod = self.productos_cache[id_producto]
            prod.nombre = nombre
            prod.cantidad = cantidad
            prod.precio = precio
            prod.categoria = categoria
            self._recalcular_categorias()

    def buscar_por_nombre(self, termino):
        # Colección: Lista obtenida por comprensión filtrando el diccionario
        return [prod for prod in self.productos_cache.values() if termino.lower() in prod.nombre.lower()]

    def obtener_por_id(self, id_producto):
        return self.productos_cache.get(id_producto)

    def mostrar_todos(self):
        # Colección: Lista a partir de los valores del diccionario
        return list(self.productos_cache.values())

    def _recalcular_categorias(self):
        # Reconstruir el conjunto de categorías únicas a partir de los productos actuales
        self.categorias_unicas = {prod.categoria for prod in self.productos_cache.values()}
