"""
Módulo para la gestión del inventario
Programación Orientada a Objetos: Herencia, Composición y Colecciones
"""

from .bd import get_db_connection
from .productos import Producto

class Inventario:
    """
    Clase que gestiona el inventario completo de productos
    Incluye sincronización automática con archivos (TXT, JSON, CSV)
    """
    def __init__(self, auto_sincronizar=True):
        # Colección: Diccionario para almacenar productos en memoria (Búsqueda rápida por ID)
        self.productos_cache = {}
        # Colección: Conjunto (Set) para almacenar categorías únicas
        self.categorias_unicas = set()
        # Controla si se sincroniza automáticamente con archivos
        self.auto_sincronizar = auto_sincronizar
        self.cargar_desde_db()

    def _sincronizar_archivos(self):
        """
        Sincroniza los datos actuales con todos los formatos de archivo
        """
        if self.auto_sincronizar:
            from .persistencia import sincronizar_todos_formatos
            productos = self.mostrar_todos()
            exito, resultados = sincronizar_todos_formatos(productos)
            return exito
        return True

    def cargar_desde_db(self):
        """
        Carga todos los productos desde la base de datos al caché en memoria
        """
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
        """
        Añade un nuevo producto al inventario (DB, memoria y archivos)
        """
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
        
        # Sincronizar con archivos
        self._sincronizar_archivos()
        
        return nuevo_producto

    def eliminar_producto(self, id_producto):
        """
        Elimina un producto del inventario (DB, memoria y archivos)
        """
        conn = get_db_connection()
        conn.execute('DELETE FROM productos WHERE id = ?', (id_producto,))
        conn.commit()
        conn.close()
        
        # Sincronizar diccionario en memoria
        if id_producto in self.productos_cache:
            del self.productos_cache[id_producto]
            self._recalcular_categorias()
        
        # Sincronizar con archivos
        self._sincronizar_archivos()

    def actualizar_producto(self, id_producto, nombre, cantidad, precio, categoria):
        """
        Actualiza un producto existente en el inventario (DB, memoria y archivos)
        """
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
        
        # Sincronizar con archivos
        self._sincronizar_archivos()

    def buscar_por_nombre(self, termino):
        """
        Busca productos por nombre (búsqueda parcial)
        Colección: Lista obtenida por comprensión filtrando el diccionario
        """
        return [prod for prod in self.productos_cache.values() if termino.lower() in prod.nombre.lower()]

    def obtener_por_id(self, id_producto):
        """
        Obtiene un producto específico por su ID
        """
        return self.productos_cache.get(id_producto)

    def mostrar_todos(self):
        """
        Retorna todos los productos del inventario
        Colección: Lista a partir de los valores del diccionario
        """
        return list(self.productos_cache.values())

    def _recalcular_categorias(self):
        """
        Reconstruye el conjunto de categorías únicas a partir de los productos actuales
        """
        self.categorias_unicas = {prod.categoria for prod in self.productos_cache.values()}
