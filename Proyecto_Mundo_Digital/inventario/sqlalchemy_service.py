"""
Servicio de datos con SQLAlchemy
Capa de acceso a datos usando SQLAlchemy ORM
"""

from .models import ProductoModel, HistorialModel, get_session, close_session, init_sqlalchemy_db
from datetime import datetime


class ProductoService:
    """
    Servicio para gestionar productos usando SQLAlchemy
    Implementa operaciones CRUD con el ORM
    """
    
    @staticmethod
    def crear_producto(nombre, cantidad, precio, categoria, descripcion=None):
        """
        Crear un nuevo producto en la base de datos usando SQLAlchemy
        """
        session = get_session()
        try:
            # Crear instancia del modelo
            nuevo_producto = ProductoModel(
                nombre=nombre,
                cantidad=cantidad,
                precio=precio,
                categoria=categoria,
                descripcion=descripcion
            )
            
            # Agregar a la sesión y confirmar
            session.add(nuevo_producto)
            session.commit()
            
            # Registrar en historial
            ProductoService._registrar_historial(
                session,
                nuevo_producto.id,
                'crear',
                f'Producto "{nombre}" creado'
            )
            session.commit()
            
            # Refrescar para obtener datos actualizados
            session.refresh(nuevo_producto)
            
            return True, nuevo_producto
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def obtener_producto(producto_id):
        """
        Obtener un producto por su ID usando SQLAlchemy
        """
        session = get_session()
        try:
            producto = session.query(ProductoModel).filter_by(id=producto_id).first()
            return producto
        finally:
            session.close()
    
    @staticmethod
    def obtener_todos_productos():
        """
        Obtener todos los productos de la base de datos
        """
        session = get_session()
        try:
            productos = session.query(ProductoModel).all()
            return productos
        finally:
            session.close()
    
    @staticmethod
    def buscar_productos(termino):
        """
        Buscar productos por nombre o categoría usando SQLAlchemy
        """
        session = get_session()
        try:
            productos = session.query(ProductoModel).filter(
                (ProductoModel.nombre.contains(termino)) |
                (ProductoModel.categoria.contains(termino))
            ).all()
            return productos
        finally:
            session.close()
    
    @staticmethod
    def actualizar_producto(producto_id, **kwargs):
        """
        Actualizar un producto existente usando SQLAlchemy
        """
        session = get_session()
        try:
            producto = session.query(ProductoModel).filter_by(id=producto_id).first()
            
            if not producto:
                return False, "Producto no encontrado"
            
            # Actualizar campos proporcionados
            cambios = []
            for key, value in kwargs.items():
                if hasattr(producto, key) and value is not None:
                    setattr(producto, key, value)
                    cambios.append(f"{key}={value}")
            
            producto.fecha_actualizacion = datetime.utcnow()
            
            # Registrar en historial
            ProductoService._registrar_historial(
                session,
                producto_id,
                'actualizar',
                f'Producto actualizado: {", ".join(cambios)}'
            )
            
            session.commit()
            return True, producto
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def eliminar_producto(producto_id):
        """
        Eliminar un producto de la base de datos usando SQLAlchemy
        """
        session = get_session()
        try:
            producto = session.query(ProductoModel).filter_by(id=producto_id).first()
            
            if not producto:
                return False, "Producto no encontrado"
            
            nombre = producto.nombre
            
            # Registrar en historial antes de eliminar
            ProductoService._registrar_historial(
                session,
                producto_id,
                'eliminar',
                f'Producto "{nombre}" eliminado'
            )
            
            # Eliminar el producto
            session.delete(producto)
            session.commit()
            
            return True, f"Producto '{nombre}' eliminado correctamente"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    @staticmethod
    def obtener_por_categoria(categoria):
        """
        Obtener productos de una categoría específica
        """
        session = get_session()
        try:
            productos = session.query(ProductoModel).filter_by(categoria=categoria).all()
            return productos
        finally:
            session.close()
    
    @staticmethod
    def obtener_estadisticas():
        """
        Obtener estadísticas completas del inventario usando SQLAlchemy
        """
        session = get_session()
        try:
            from sqlalchemy import func
            
            total_productos = session.query(func.count(ProductoModel.id)).scalar() or 0
            total_stock = session.query(func.sum(ProductoModel.cantidad)).scalar() or 0
            valor_inventario = session.query(
                func.sum(ProductoModel.cantidad * ProductoModel.precio)
            ).scalar() or 0.0
            
            # Promedios
            precio_promedio = session.query(func.avg(ProductoModel.precio)).scalar() or 0.0
            stock_promedio = session.query(func.avg(ProductoModel.cantidad)).scalar() or 0.0
            
            # Categorías únicas
            categorias = session.query(ProductoModel.categoria).distinct().all()
            categorias = [c[0] for c in categorias]
            
            # Productos por estado
            productos_disponibles = session.query(ProductoModel).filter(ProductoModel.cantidad > 10).count()
            productos_poco_stock = session.query(ProductoModel).filter(
                ProductoModel.cantidad > 0, ProductoModel.cantidad <= 10
            ).count()
            productos_agotados = session.query(ProductoModel).filter(ProductoModel.cantidad == 0).count()
            
            # Productos destacados
            producto_mayor_valor = session.query(ProductoModel)\
                .order_by((ProductoModel.cantidad * ProductoModel.precio).desc())\
                .first()
            
            producto_mayor_stock = session.query(ProductoModel)\
                .order_by(ProductoModel.cantidad.desc())\
                .first()
            
            producto_mayor_precio = session.query(ProductoModel)\
                .order_by(ProductoModel.precio.desc())\
                .first()
            
            # Productos por categoría con estadísticas
            productos_por_categoria = session.query(
                ProductoModel.categoria,
                func.count(ProductoModel.id).label('total'),
                func.sum(ProductoModel.cantidad).label('total_stock'),
                func.sum(ProductoModel.cantidad * ProductoModel.precio).label('valor_total')
            ).group_by(ProductoModel.categoria).all()
            
            productos_por_categoria_dict = [
                {
                    'categoria': cat,
                    'total': total,
                    'total_stock': total_stock or 0,
                    'valor_total': round(valor_total or 0.0, 2)
                }
                for cat, total, total_stock, valor_total in productos_por_categoria
            ]
            
            return {
                'total_productos': total_productos,
                'total_stock': total_stock,
                'valor_inventario': round(valor_inventario, 2),
                'categorias': categorias,
                'num_categorias': len(categorias),
                'productos_disponibles': productos_disponibles,
                'productos_poco_stock': productos_poco_stock,
                'productos_agotados': productos_agotados,
                'precio_promedio': round(precio_promedio, 2),
                'stock_promedio': round(stock_promedio, 1),
                'valor_promedio': round(valor_inventario / total_productos, 2) if total_productos > 0 else 0.0,
                'rotacion': round((productos_disponibles / total_productos * 100), 1) if total_productos > 0 else 0.0,
                'producto_mayor_valor': producto_mayor_valor,
                'producto_mayor_stock': producto_mayor_stock,
                'producto_mayor_precio': producto_mayor_precio,
                'productos_por_categoria': productos_por_categoria_dict
            }
        finally:
            session.close()
    
    @staticmethod
    def _registrar_historial(session, producto_id, accion, descripcion):
        """
        Registrar una acción en el historial (método interno)
        """
        historial = HistorialModel(
            producto_id=producto_id,
            accion=accion,
            descripcion=descripcion
        )
        session.add(historial)


class HistorialService:
    """
    Servicio para gestionar el historial de cambios
    """
    
    @staticmethod
    def obtener_historial(limite=50):
        """
        Obtener el historial de cambios recientes
        """
        session = get_session()
        try:
            historial = session.query(HistorialModel)\
                              .order_by(HistorialModel.fecha.desc())\
                              .limit(limite)\
                              .all()
            return historial
        finally:
            session.close()
    
    @staticmethod
    def obtener_historial_producto(producto_id):
        """
        Obtener el historial de un producto específico
        """
        session = get_session()
        try:
            historial = session.query(HistorialModel)\
                              .filter_by(producto_id=producto_id)\
                              .order_by(HistorialModel.fecha.desc())\
                              .all()
            return historial
        finally:
            session.close()
    
    @staticmethod
    def obtener_estadisticas_historial():
        """
        Obtener estadísticas del historial de cambios
        """
        session = get_session()
        try:
            from sqlalchemy import func
            
            total_crear = session.query(func.count(HistorialModel.id))\
                                .filter_by(accion='crear')\
                                .scalar() or 0
            
            total_actualizar = session.query(func.count(HistorialModel.id))\
                                     .filter_by(accion='actualizar')\
                                     .scalar() or 0
            
            total_eliminar = session.query(func.count(HistorialModel.id))\
                                   .filter_by(accion='eliminar')\
                                   .scalar() or 0
            
            return {
                'total_crear': total_crear,
                'total_actualizar': total_actualizar,
                'total_eliminar': total_eliminar
            }
        finally:
            session.close()
