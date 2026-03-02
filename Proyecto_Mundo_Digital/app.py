from flask import Flask, render_template, request, redirect, url_for
from inventario import init_db, Inventario

app = Flask(__name__)

# Inicializar Base de Datos e Inventario (POO)
init_db()
sistema_inventario = Inventario()

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
def agregar_producto(producto):
    return f'Producto {producto} agregado al carrito'

@app.route('/carrito/eliminar/<producto>')
def eliminar_producto(producto):
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

if __name__ == '__main__':
    app.run(debug=True)