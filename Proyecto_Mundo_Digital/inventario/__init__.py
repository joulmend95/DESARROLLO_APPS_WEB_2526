# Módulo de Inventario
# Importaciones para facilitar el uso del módulo

from .bd import get_db_connection, init_db
from .productos import Producto, ESTADOS_PRODUCTO
from .inventario import Inventario
from .persistencia import (
    guardar_txt, leer_txt,
    guardar_json, leer_json,
    guardar_csv, leer_csv,
    sincronizar_todos_formatos, leer_todos_formatos,
    cargar_desde_archivo
)

# SQLAlchemy imports
from .models import (
    ProductoModel, HistorialModel, 
    init_sqlalchemy_db, get_session, close_session
)
from .sqlalchemy_service import ProductoService, HistorialService

__all__ = [
    # SQLite básico
    'get_db_connection', 'init_db', 'Producto', 'ESTADOS_PRODUCTO', 'Inventario',
    # Persistencia
    'guardar_txt', 'leer_txt', 'guardar_json', 'leer_json',
    'guardar_csv', 'leer_csv', 'sincronizar_todos_formatos',
    'leer_todos_formatos', 'cargar_desde_archivo',
    # SQLAlchemy
    'ProductoModel', 'HistorialModel', 'init_sqlalchemy_db',
    'get_session', 'close_session', 'ProductoService', 'HistorialService'
]
