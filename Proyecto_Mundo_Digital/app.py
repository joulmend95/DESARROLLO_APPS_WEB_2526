from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import json
import csv
import os
from fpdf import FPDF
from io import BytesIO
from inventario import (
    init_db, Inventario, crear_pedido, obtener_pedidos, obtener_pedido_con_detalles
)
from dotenv import load_dotenv

load_dotenv()

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from inventario.models import UsuarioModel
from Conexion.conexion import get_db_connection

app = Flask(__name__)

# Configuración Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return UsuarioModel(user['id_usuario'], user['nombre'], user['email'], user['password'], user['rol'])
    return None
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_fallback_key_dev_only')

# Inicializar Base de Datos SQLite bÃ¡sica e Inventario (POO)
init_db()
sistema_inventario = Inventario(auto_sincronizar=True)

@app.before_request
def restrict_admin_access():
    # Permitir acceso siempre a archivos estáticos
    if request.endpoint and request.endpoint.startswith('static'):
        return

    if current_user.is_authenticated and current_user.rol == 'admin':
        # Lista de endpoints permitidos para el admin
        admin_endpoints = [
            'listar_inventario', 'buscar_inventario', 'agregar_inventario',
            'editar_inventario', 'eliminar_inventario', 'exportar_pdf', 'logout'
        ]
        if request.endpoint and request.endpoint not in admin_endpoints:
            return redirect(url_for('listar_inventario'))

@app.route('/')
def home():
    if current_user.is_authenticated and current_user.rol == 'admin':
        return redirect(url_for('listar_inventario'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.rol == 'admin':
            return redirect(url_for('listar_inventario'))
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                usuario_obj = UsuarioModel(user['id_usuario'], user['nombre'], user['email'], user['password'], user['rol'])
                login_user(usuario_obj)
                flash('Sesión iniciada exitosamente.', 'success')
                
                next_page = request.args.get('next')
                if not next_page:
                    if usuario_obj.rol == 'admin':
                        return redirect(url_for('listar_inventario'))
                    else:
                        return redirect(url_for('home'))
                return redirect(next_page)
            else:
                flash('Correo o contraseña incorrectos.', 'error')
                
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # Verificar si existe el email
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('El correo ya está registrado.', 'error')
            else:
                try:
                    cursor.execute(
                        "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)",
                        (nombre, email, hashed_password, 'cliente')
                    )
                    conn.commit()
                    flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
                    
                    next_page = request.args.get('next')
                    return redirect(url_for('login', next=next_page) if next_page else url_for('login'))
                except Exception as e:
                    conn.rollback()
                    flash(f'Error al registrar: {str(e)}', 'error')
                finally:
                    cursor.close()
                    conn.close()
                    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/catalogo')
def catalogo():
    productos = sistema_inventario.mostrar_todos()
    return render_template('catalogo.html', productos=productos)

@app.route('/carrito')
def carrito():
    carrito_items = session.get('carrito', {})
    total = sum(float(item['precio']) * int(item['cantidad']) for item in carrito_items.values())
    return render_template('carrito.html', carrito=carrito_items, total=total)

@app.route('/carrito/agregar/<int:id_producto>', methods=['POST'])
def agregar_al_carrito(id_producto):
    producto = sistema_inventario.obtener_por_id(id_producto)
    if not producto:
        flash("Producto no encontrado", "error")
        return redirect(url_for('catalogo'))
        
    if 'carrito' not in session:
        session['carrito'] = {}
        
    carrito = session['carrito']
    id_str = str(id_producto)
    
    # Obtener atributos independientemente de si es objeto o dict
    stock_disponible = getattr(producto, 'cantidad', None) 
    if stock_disponible is None:
        stock_disponible = producto.get('cantidad', 0)
        
    # Cantidad solicitada desde el formulario, o 1 por defecto
    try:
        cantidad_solicitada = int(request.form.get('cantidad', 1))
    except ValueError:
        cantidad_solicitada = 1

    if cantidad_solicitada <= 0:
        flash("La cantidad debe ser mayor a 0.", "error")
        return redirect(url_for('catalogo'))

    cantidad_actual = carrito.get(id_str, {}).get('cantidad', 0)
    nueva_cantidad = cantidad_actual + cantidad_solicitada
    
    if nueva_cantidad > stock_disponible:
        flash(f"No hay suficiente stock. Stock disponible: {stock_disponible}", "error")
        return redirect(url_for('catalogo'))
    
    if id_str in carrito:
        carrito[id_str]['cantidad'] = nueva_cantidad
    else:
        nombre = getattr(producto, 'nombre', None) or producto['nombre']
        precio = getattr(producto, 'precio', None) or producto['precio']
        
        carrito[id_str] = {
            'id': id_producto,
            'nombre': nombre,
            'precio': precio,
            'cantidad': nueva_cantidad
        }
        
    session.modified = True
    flash(f"Se agregaron {cantidad_solicitada} unidad(es) de {getattr(producto, 'nombre', None) or producto.get('nombre')} al carrito.", "success")
    return redirect(url_for('catalogo'))

@app.route('/carrito/eliminar/<int:id_producto>', methods=['POST'])
def eliminar_del_carrito(id_producto):
    carrito = session.get('carrito', {})
    id_str = str(id_producto)
    
    if id_str in carrito:
        del carrito[id_str]
        session.modified = True
        flash("Producto eliminado del carrito.", "success")
        
    return redirect(url_for('carrito'))

@app.route('/checkout')
@login_required
def checkout():
    carrito_items = session.get('carrito', {})
    if not carrito_items:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for('catalogo'))
        
    total = sum(float(item['precio']) * int(item['cantidad']) for item in carrito_items.values())
    return render_template('checkout.html', carrito=carrito_items, total=total)

@app.route('/checkout/confirmar', methods=['POST'])
@login_required
def confirmar_checkout():
    carrito = session.get('carrito', {})
    if not carrito:
        flash("Tu carrito está vacío.", "error")
        return redirect(url_for('catalogo'))

    # Si está logueado, cogemos los datos del usuario actual
    cliente_nombre = current_user.nombre
    cliente_email = current_user.email
    total = sum(float(item['precio']) * int(item['cantidad']) for item in carrito.values())

    # Registrar el pedido en la BD y en los ficheros CSV/JSON/TXT
    pedido_id = crear_pedido(cliente_nombre, cliente_email, total, carrito)

    # Reducir el stock en el inventario
    for id_str, item in carrito.items():
        producto = sistema_inventario.obtener_por_id(item['id'])
        if producto:
            stock_actual = getattr(producto, 'cantidad', None)
            if stock_actual is None:
                stock_actual = producto.get('cantidad', 0)

            nuevo_stock = max(0, stock_actual - item['cantidad'])

            # Necesitamos todos los datos para actualizar
            nombre = getattr(producto, 'nombre', None) or producto['nombre']
            precio = getattr(producto, 'precio', None) or producto['precio']
            categoria = getattr(producto, 'categoria', None) or producto.get('categoria', 'General')
            sistema_inventario.actualizar_producto(item['id'], nombre, nuevo_stock, precio, categoria)

    # Vaciar el carrito
    session.pop('carrito', None)
    session.modified = True

    if pedido_id:
        return redirect(url_for('ver_factura', pedido_id=pedido_id))
    else:
        return render_template('confirmar_checkout.html')

@app.route('/pedidos')
@login_required
def lista_pedidos():
    pedidos = obtener_pedidos()
    return render_template('pedidos.html', pedidos=pedidos)

@app.route('/factura/<int:pedido_id>')
@login_required
def ver_factura(pedido_id):
    pedido, detalles = obtener_pedido_con_detalles(pedido_id)
    if not pedido:
        flash("Pedido no encontrado", "error")
        return redirect(url_for('home'))
    return render_template('factura.html', pedido=pedido, detalles=detalles)

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

# ================================
# Rutas CRUD de Inventario (POO & SQLite)
# ================================

@app.route('/inventario')
def listar_inventario():
    # ColecciÃ³n (Lista) proveniente de la clase Inventario
    productos = sistema_inventario.mostrar_todos()
    # ColecciÃ³n (Set)
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
    
    # AÃ±adir vÃ­a POO y SQLite
    sistema_inventario.añadir_producto(nombre, cantidad, precio, categoria)
    return redirect(url_for('listar_inventario'))

@app.route('/inventario/editar/<int:id_producto>', methods=['GET', 'POST'])
def editar_inventario(id_producto):
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        categoria = request.form.get('categoria', 'General')
        
        # Sincronizar actualizaciÃ³n
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

@app.route('/inventario/reporte_pdf')
def exportar_pdf():
    # Obtener el listado de productos
    productos = sistema_inventario.mostrar_todos()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título
    pdf.cell(200, 10, txt="Reporte de Inventario", ln=True, align='C')
    pdf.ln(10)

    # Encabezados de tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(10, 10, 'ID', 1, 0, 'C')
    pdf.cell(70, 10, 'Nombre', 1, 0, 'C')
    pdf.cell(25, 10, 'Cantidad', 1, 0, 'C')
    pdf.cell(30, 10, 'Precio ($)', 1, 0, 'C')
    pdf.cell(50, 10, 'Categoria', 1, 1, 'C')

    # Filas de la tabla
    pdf.set_font("Arial", '', 10)
    for p in productos:
        # Asegurarse de quitar o manejar los caracteres no soportados por fpdf
        nombre = p.nombre.encode('latin-1', 'replace').decode('latin-1')
        cat = p.categoria.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.cell(10, 10, str(p.id), 1, 0, 'C')
        pdf.cell(70, 10, nombre, 1, 0, 'L')
        pdf.cell(25, 10, str(p.cantidad), 1, 0, 'C')
        pdf.cell(30, 10, f"{p.precio:.2f}", 1, 0, 'C')
        pdf.cell(50, 10, cat, 1, 1, 'L')

    # Guardar en buffer en memoria y enviar
    pdf_val = pdf.output(dest='S').encode('latin-1')
    pdf_buffer = BytesIO(pdf_val)
    
    return send_file(
        pdf_buffer, 
        as_attachment=True, 
        download_name='Reporte_Inventario.pdf', 
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)





