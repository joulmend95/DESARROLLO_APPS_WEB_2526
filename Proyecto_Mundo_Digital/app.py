from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bienvenido a tu tienda online ¡Mundo Digital!'

@app.route('/producto/<nombre>')
def producto(nombre):
    return f'Producto: {nombre}! - diponible en nuestra tienda online' 

@app.route('/catalogo')
def catalogo():
    productos = ['Laptop Asus', 'Laptop Lenovo', 'Mouse Logitech', 'Auriculares Soundcore']
    return f'Catálogo de productos: {", ".join(productos)}'

@app.route('/carrito')
def carrito():
    return 'Carrito de compras'

@app.route('/carrito/agregar/<producto>')
def agregar_producto(producto):
    return f'Producto {producto} agregado al carrito'

@app.route('/carrito/eliminar/<producto>')
def eliminar_producto(producto):
    return f'Producto {producto} eliminado del carrito'

@app.route('/checkout')
def checkout():
    return 'Proceso de pago'

@app.route('/checkout/confirmar')
def confirmar_checkout():
    return 'Compra confirmada'

@app.route('/contacto')
def contacto():
    return 'Información de contacto'

if __name__ == '__main__':
    app.run(debug=True)