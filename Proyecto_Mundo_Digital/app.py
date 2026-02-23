from flask import Flask, render_template
app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)