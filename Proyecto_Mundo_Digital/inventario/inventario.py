"""
MÃ³dulo para la gestiÃ³n del inventario
ProgramaciÃ³n Orientada a Objetos: Herencia, ComposiciÃ³n y Colecciones
"""

from Conexion.conexion import get_db_connection
from .productos import Producto

class Inventario:
    """
    Clase que gestiona el inventario completo de productos
    Incluye sincronizaciÃ³n automÃ¡tica con archivos (TXT, JSON, CSV)
    """
    def __init__(self, auto_sincronizar=True):
        # ColecciÃ³n: Diccionario para almacenar productos en memoria (BÃºsqueda rÃ¡pida por ID)
        self.productos_cache = {}
        # ColecciÃ³n: Conjunto (Set) para almacenar categorÃ­as Ãºnicas
        self.categorias_unicas = set()
        # Controla si se sincroniza automÃ¡ticamente con archivos
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
        Carga todos los productos desde la base de datos al cachÃ© en memoria
        """
        self.productos_cache.clear()
        self.categorias_unicas.clear()
        conn = get_db_connection()
        if conn:
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT * FROM productos')
            rows = cur.fetchall()
            for row in rows:
                prod = Producto(row['id'], row['nombre'], row['cantidad'], row['precio'], row['categoria'])
                self.productos_cache[prod.id] = prod
                self.categorias_unicas.add(prod.categoria)
            cur.close()
            conn.close()

    def añadir_producto(self, nombre, cantidad, precio, categoria):
        """
        AÃ±ade un nuevo producto al inventario (DB, memoria y archivos)
        """
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO productos (nombre, cantidad, precio, categoria) VALUES (%s, %s, %s, %s)',
                        (nombre, cantidad, precio, categoria))
            conn.commit()
            nuevo_id = cur.lastrowid
            cur.close()
            conn.close()
        else:
            nuevo_id = len(self.productos_cache) + 1
        
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
        if conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM productos WHERE id = %s', (id_producto,))
            conn.commit()
            cur.close()
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
        if conn:
            cur = conn.cursor()
            cur.execute('UPDATE productos SET nombre = %s, cantidad = %s, precio = %s, categoria = %s WHERE id = %s',
                        (nombre, cantidad, precio, categoria, id_producto))
            conn.commit()
            cur.close()
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
        Busca productos por nombre (bÃºsqueda parcial)
        ColecciÃ³n: Lista obtenida por comprensiÃ³n filtrando el diccionario
        """
        return [prod for prod in self.productos_cache.values() if termino.lower() in prod.nombre.lower()]

    def obtener_por_id(self, id_producto):
        """
        Obtiene un producto especÃ­fico por su ID
        """
        return self.productos_cache.get(id_producto)

    def mostrar_todos(self):
        """
        Retorna todos los productos del inventario
        ColecciÃ³n: Lista a partir de los valores del diccionario
        """
        return list(self.productos_cache.values())

    def _recalcular_categorias(self):
        """
        Reconstruye el conjunto de categorÃ­as Ãºnicas a partir de los productos actuales
        """
        self.categorias_unicas = {prod.categoria for prod in self.productos_cache.values()}

