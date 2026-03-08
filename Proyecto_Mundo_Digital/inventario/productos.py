"""
Módulo para la definición de la clase Producto
Programación Orientada a Objetos: Encapsulación, Properties y Decoradores
"""

# Constantes (Tupla)
ESTADOS_PRODUCTO = ("Disponible", "Agotado", "Descontinuado")

class Producto:
    """
    Clase que representa un producto en el inventario
    """
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
        """
        Retorna el estado del producto según la cantidad disponible
        Uso de tuplas para condiciones
        """
        if self._cantidad > 0:
            return ESTADOS_PRODUCTO[0]
        return ESTADOS_PRODUCTO[1]

    def a_diccionario(self):
        """
        Convierte el producto a un diccionario para facilitar su uso
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'cantidad': self.cantidad,
            'precio': self.precio,
            'categoria': self.categoria,
            'estado': self.estado()
        }
