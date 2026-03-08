from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import json
import csv
import os
from inventario import (
    init_db, Inventario,
    leer_txt, leer_json, leer_csv,
    guardar_txt, guardar_json, guardar_csv,
    cargar_desde_archivo,
    # SQLAlchemy
    init_sqlalchemy_db, ProductoService, HistorialService
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui_cambiar_en_produccion'

# Inicializar Base de Datos SQLite básica e Inventario (POO)
init_db()
sistema_inventario = Inventario(auto_sincronizar=True)

# Inicializar Base de Datos SQLAlchemy
init_sqlalchemy_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/catalogo')
def catalogo():
    lista_productos = ['Laptop Asus', 'Laptop Lenovo', 'Mouse Logitech', 'Auriculares Soundcore']
    return render_template('catalogo.html', productos=lista_productos)

@app.route('/carrito')
def carrito():
    return render_template('carrito.html')

@app.route('/carrito/agregar/<producto>')
def agregar_al_carrito(producto):
    return f'Producto {producto} agregado al carrito'

@app.route('/carrito/eliminar/<producto>')
def eliminar_del_carrito(producto):
    return f'Producto {producto} eliminado del carrito'

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/checkout/confirmar')
def confirmar_checkout():
    return render_template('confirmar_checkout.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/contactos')
def contactos():
    return render_template('contactos.html')

# ================================
# Rutas CRUD de Inventario (POO & SQLite)
# ================================

@app.route('/inventario')
def listar_inventario():
    # Colección (Lista) proveniente de la clase Inventario
    productos = sistema_inventario.mostrar_todos()
    # Colección (Set)
    categorias = sistema_inventario.categorias_unicas
    return render_template('inventario.html', productos=productos, categorias=categorias)

@app.route('/inventario/buscar', methods=['GET'])
def buscar_inventario():
    termino = request.args.get('busqueda', '')
    if termino:
        productos = sistema_inventario.buscar_por_nombre(termino)
    else:
        productos = sistema_inventario.mostrar_todos()
    categorias = sistema_inventario.categorias_unicas
    return render_template('inventario.html', productos=productos, categorias=categorias, busqueda=termino)

@app.route('/inventario/agregar', methods=['POST'])
def agregar_inventario():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    precio = float(request.form['precio'])
    categoria = request.form.get('categoria', 'General')
    
    # Añadir vía POO y SQLite
    sistema_inventario.añadir_producto(nombre, cantidad, precio, categoria)
    return redirect(url_for('listar_inventario'))

@app.route('/inventario/editar/<int:id_producto>', methods=['GET', 'POST'])
def editar_inventario(id_producto):
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        categoria = request.form.get('categoria', 'General')
        
        # Sincronizar actualización
        sistema_inventario.actualizar_producto(id_producto, nombre, cantidad, precio, categoria)
        return redirect(url_for('listar_inventario'))
    else:
        producto_a_editar = sistema_inventario.obtener_por_id(id_producto)
        productos = sistema_inventario.mostrar_todos()
        categorias = sistema_inventario.categorias_unicas
        return render_template('inventario.html', productos=productos, categorias=categorias, editar=producto_a_editar)

@app.route('/inventario/eliminar/<int:id_producto>')
def eliminar_inventario(id_producto):
    sistema_inventario.eliminar_producto(id_producto)
    return redirect(url_for('listar_inventario'))

# ================================
# Rutas de Productos (alternativa a inventario)
# ================================

@app.route('/productos')
def listar_productos():
    productos = sistema_inventario.mostrar_todos()
    categorias = sistema_inventario.categorias_unicas
    return render_template('productos.html', productos=productos, categorias=categorias)

@app.route('/productos/buscar', methods=['GET'])
def buscar_productos():
    termino = request.args.get('busqueda', '')
    if termino:
        productos = sistema_inventario.buscar_por_nombre(termino)
    else:
        productos = sistema_inventario.mostrar_todos()
    categorias = sistema_inventario.categorias_unicas
    return render_template('productos.html', productos=productos, categorias=categorias, busqueda=termino)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        categoria = request.form.get('categoria', 'General')
        sistema_inventario.añadir_producto(nombre, cantidad, precio, categoria)
        return redirect(url_for('listar_productos'))
    return render_template('producto_form.html')

@app.route('/productos/editar/<int:id_producto>', methods=['GET', 'POST'])
def editar_producto(id_producto):
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        categoria = request.form.get('categoria', 'General')
        sistema_inventario.actualizar_producto(id_producto, nombre, cantidad, precio, categoria)
        return redirect(url_for('listar_productos'))
    else:
        producto = sistema_inventario.obtener_por_id(id_producto)
        return render_template('producto_form.html', producto=producto)

@app.route('/productos/eliminar/<int:id_producto>')
def eliminar_producto(id_producto):
    sistema_inventario.eliminar_producto(id_producto)
    return redirect(url_for('listar_productos'))

# ================================
# Rutas de Persistencia de Datos (Semana 12)
# ================================

@app.route('/datos')
def ver_datos():
    """
    Muestra los datos almacenados en los archivos TXT, JSON y CSV
    Utiliza las funciones de persistencia del módulo inventario
    """
    # Leer datos TXT usando la función open() en modo lectura
    datos_txt_lista = leer_txt()
    datos_txt = None
    txt_path = os.path.join('inventario', 'data', 'datos.txt')
    if os.path.exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8') as f:
            datos_txt = f.read()
    
    # Leer datos JSON usando la librería json
    datos_json = leer_json()
    
    # Leer datos CSV usando la librería csv
    datos_csv_lista = leer_csv()
    
    # Convertir CSV a formato de tabla para la plantilla
    datos_csv = None
    if datos_csv_lista:
        # Crear encabezados y filas
        datos_csv = [
            ['id', 'nombre', 'cantidad', 'precio', 'categoria', 'estado']
        ]
        for producto in datos_csv_lista:
            datos_csv.append([
                producto['id'],
                producto['nombre'],
                producto['cantidad'],
                producto['precio'],
                producto['categoria'],
                producto.get('estado', 'Desconocido')
            ])
    
    return render_template('datos.html', 
                         datos_txt=datos_txt, 
                         datos_json={'productos': datos_json} if datos_json else None, 
                         datos_csv=datos_csv)


@app.route('/datos/formato/<formato>')
def ver_formato(formato):
    """
    Muestra los datos de un formato específico
    """
    if formato == 'txt':
        productos = leer_txt()
        return render_template('formato_txt.html', productos=productos)
    elif formato == 'json':
        productos = leer_json()
        return render_template('formato_json.html', productos=productos)
    elif formato == 'csv':
        productos = leer_csv()
        return render_template('formato_csv.html', productos=productos)
    else:
        flash('Formato no válido', 'error')
        return redirect(url_for('ver_datos'))


@app.route('/datos/importar/<formato>')
def importar_datos(formato):
    """
    Importa datos desde un archivo específico (TXT, JSON o CSV) a la base de datos
    """
    if formato not in ['txt', 'json', 'csv']:
        flash('Formato no soportado', 'error')
        return redirect(url_for('ver_datos'))
    
    exito, mensaje = cargar_desde_archivo(sistema_inventario, formato)
    
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'error')
    
    return redirect(url_for('listar_productos'))


@app.route('/datos/sincronizar')
def sincronizar_datos():
    """
    Sincroniza los datos actuales de la base de datos con todos los archivos
    """
    productos = sistema_inventario.mostrar_todos()
    
    # Usar las funciones de persistencia
    exito_txt, msg_txt = guardar_txt(productos)
    exito_json, msg_json = guardar_json(productos)
    exito_csv, msg_csv = guardar_csv(productos)
    
    if exito_txt and exito_json and exito_csv:
        flash('Datos sincronizados correctamente en todos los formatos', 'success')
    else:
        flash('Hubo problemas al sincronizar algunos formatos', 'warning')
    
    return redirect(url_for('ver_datos'))

@app.route('/datos/exportar/<formato>')
def exportar_datos(formato):
    """
    Exporta los datos del inventario actual a TXT, JSON o CSV
    Utiliza las funciones de persistencia del módulo
    """
    productos = sistema_inventario.mostrar_todos()
    
    if formato == 'txt':
        # Exportar a TXT usando la función guardar_txt
        guardar_txt(productos)
        txt_path = os.path.join('inventario', 'data', 'datos.txt')
        return send_file(txt_path, as_attachment=True, download_name='inventario.txt')
    
    elif formato == 'json':
        # Exportar a JSON usando la función guardar_json
        guardar_json(productos)
        json_path = os.path.join('inventario', 'data', 'datos.json')
        return send_file(json_path, as_attachment=True, download_name='inventario.json')
    
    elif formato == 'csv':
        # Exportar a CSV usando la función guardar_csv
        guardar_csv(productos)
        csv_path = os.path.join('inventario', 'data', 'datos.csv')
        return send_file(csv_path, as_attachment=True, download_name='inventario.csv')
    
    return redirect(url_for('ver_datos'))


# ================================
# Rutas de SQLAlchemy (Semana 12)
# ================================

@app.route('/sqlalchemy')
def sqlalchemy_home():
    """
    Página principal de SQLAlchemy mostrando productos
    """
    productos = ProductoService.obtener_todos_productos()
    estadisticas = ProductoService.obtener_estadisticas()
    return render_template('sqlalchemy_home.html', 
                         productos=productos, 
                         estadisticas=estadisticas)


@app.route('/sqlalchemy/crear', methods=['GET', 'POST'])
def sqlalchemy_crear():
    """
    Crear un nuevo producto usando SQLAlchemy
    """
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        cantidad = int(request.form.get('cantidad', 0))
        precio = float(request.form.get('precio', 0.0))
        categoria = request.form.get('categoria')
        descripcion = request.form.get('descripcion', '')
        
        exito, resultado = ProductoService.crear_producto(
            nombre, cantidad, precio, categoria, descripcion
        )
        
        if exito:
            flash(f'Producto "{nombre}" creado exitosamente con SQLAlchemy', 'success')
            return redirect(url_for('sqlalchemy_home'))
        else:
            flash(f'Error al crear producto: {resultado}', 'error')
    
    return render_template('sqlalchemy_form.html', accion='crear')


@app.route('/sqlalchemy/editar/<int:producto_id>', methods=['GET', 'POST'])
def sqlalchemy_editar(producto_id):
    """
    Editar un producto existente usando SQLAlchemy
    """
    if request.method == 'POST':
        datos = {
            'nombre': request.form.get('nombre'),
            'cantidad': int(request.form.get('cantidad', 0)),
            'precio': float(request.form.get('precio', 0.0)),
            'categoria': request.form.get('categoria'),
            'descripcion': request.form.get('descripcion')
        }
        
        exito, resultado = ProductoService.actualizar_producto(producto_id, **datos)
        
        if exito:
            flash(f'Producto actualizado exitosamente con SQLAlchemy', 'success')
            return redirect(url_for('sqlalchemy_home'))
        else:
            flash(f'Error al actualizar: {resultado}', 'error')
    
    # GET - Mostrar formulario con datos actuales
    producto = ProductoService.obtener_producto(producto_id)
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('sqlalchemy_home'))
    
    return render_template('sqlalchemy_form.html', 
                         accion='editar', 
                         producto=producto)


@app.route('/sqlalchemy/eliminar/<int:producto_id>')
def sqlalchemy_eliminar(producto_id):
    """
    Eliminar un producto usando SQLAlchemy
    """
    exito, mensaje = ProductoService.eliminar_producto(producto_id)
    
    if exito:
        flash(mensaje, 'success')
    else:
        flash(f'Error: {mensaje}', 'error')
    
    return redirect(url_for('sqlalchemy_home'))


@app.route('/sqlalchemy/buscar')
def sqlalchemy_buscar():
    """
    Buscar productos usando SQLAlchemy
    """
    termino = request.args.get('q', '')
    estadisticas = ProductoService.obtener_estadisticas()
    
    if termino:
        productos = ProductoService.buscar_productos(termino)
        flash(f'Se encontraron {len(productos)} productos con "{termino}"', 'info')
    else:
        productos = ProductoService.obtener_todos_productos()
    
    return render_template('sqlalchemy_home.html', 
                         productos=productos,
                         estadisticas=estadisticas,
                         termino_busqueda=termino)


@app.route('/sqlalchemy/detalle/<int:producto_id>')
def sqlalchemy_detalle(producto_id):
    """
    Ver detalle de un producto con su historial usando SQLAlchemy
    """
    producto = ProductoService.obtener_producto(producto_id)
    
    if not producto:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('sqlalchemy_home'))
    
    # Obtener historial del producto
    historial = HistorialService.obtener_historial_producto(producto_id)
    
    return render_template('sqlalchemy_detalle.html', 
                         producto=producto,
                         historial=historial)


@app.route('/sqlalchemy/historial')
def sqlalchemy_historial():
    """
    Ver el historial completo de cambios
    """
    historial = HistorialService.obtener_historial(limite=100)
    estadisticas = HistorialService.obtener_estadisticas_historial()
    return render_template('sqlalchemy_historial.html', 
                         historial=historial,
                         estadisticas=estadisticas)


@app.route('/sqlalchemy/estadisticas')
def sqlalchemy_estadisticas():
    """
    Ver estadísticas detalladas usando SQLAlchemy
    """
    estadisticas = ProductoService.obtener_estadisticas()
    return render_template('sqlalchemy_estadisticas.html',
                         estadisticas=estadisticas)

if __name__ == '__main__':
    app.run(debug=True)