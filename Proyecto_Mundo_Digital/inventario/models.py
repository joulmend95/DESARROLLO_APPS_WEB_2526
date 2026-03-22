"""
Modelos de Base de Datos usando SQLAlchemy ORM
Define las tablas y relaciones de la base de datos
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Crear la base declarativa
Base = declarative_base()

# ConfiguraciÃ³n de la base de datos
import os
from dotenv import load_dotenv

load_dotenv()
DB_USER = os.getenv('DB_USER', 'mundo_app_user')
DB_PASS = os.getenv('DB_PASSWORD', '123456')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_NAME = os.getenv('DB_NAME', 'mundo_digital_db')

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False)

# Crear una sesiÃ³n con scope
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


class ProductoModel(Base):
    """
    Modelo SQLAlchemy para la tabla de productos
    Representa un producto en el inventario con SQLAlchemy ORM
    """
    __tablename__ = 'productos_sqlalchemy'
    
    # DefiniciÃ³n de columnas
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, index=True)
    cantidad = Column(Integer, nullable=False, default=0)
    precio = Column(Float, nullable=False, default=0.0)
    categoria = Column(String(50), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """RepresentaciÃ³n en string del objeto"""
        return f"<ProductoModel(id={self.id}, nombre='{self.nombre}', cantidad={self.cantidad}, precio={self.precio})>"
    
    def to_dict(self):
        """
        Convierte el modelo a un diccionario para fÃ¡cil serializaciÃ³n
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'cantidad': self.cantidad,
            'precio': self.precio,
            'categoria': self.categoria,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'estado': 'Disponible' if self.cantidad > 0 else 'Agotado'
        }
    
    @property
    def estado(self):
        """Calcula el estado del producto basado en la cantidad"""
        if self.cantidad > 10:
            return 'Disponible'
        elif self.cantidad > 0:
            return 'Poco Stock'
        else:
            return 'Agotado'


class HistorialModel(Base):
    """
    Modelo SQLAlchemy para registrar el historial de cambios
    Ãštil para auditorÃ­a y seguimiento de modificaciones
    """
    __tablename__ = 'historial'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    producto_id = Column(Integer, nullable=False)
    accion = Column(String(50), nullable=False)  # 'crear', 'actualizar', 'eliminar'
    descripcion = Column(Text)
    fecha = Column(DateTime, default=datetime.utcnow)
    usuario = Column(String(50), default='sistema')
    
    def __repr__(self):
        return f"<HistorialModel(id={self.id}, accion='{self.accion}', producto_id={self.producto_id})>"
    
    def to_dict(self):
        """Convierte el historial a diccionario"""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'accion': self.accion,
            'descripcion': self.descripcion,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'usuario': self.usuario
        }


def init_sqlalchemy_db():
    """
    Inicializa la base de datos creando todas las tablas definidas
    """
    Base.metadata.create_all(bind=engine)
    print("âœ“ Base de datos SQLAlchemy inicializada correctamente")


def get_session():
    """
    Retorna una sesiÃ³n de base de datos
    Usar en un contexto 'with' para manejo automÃ¡tico
    """
    return SessionLocal()


def close_session():
    """
    Cierra la sesiÃ³n actual
    """
    SessionLocal.remove()


# Inicializar las tablas al importar el mÃ³dulo
if __name__ != '__main__':
    init_sqlalchemy_db()


from flask_login import UserMixin

class UsuarioModel(UserMixin):
    def __init__(self, id_usuario, nombre, email, password, rol):
        self.id = str(id_usuario) # Flask-Login requiere string
        self.nombre = nombre
        self.email = email
        self.password = password
        self.rol = rol

