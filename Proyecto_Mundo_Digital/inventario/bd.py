"""
Módulo para la gestión de la base de datos (Actualizado a MySQL)
"""
from Conexion.conexion import get_db_connection

def init_db():
    """
    Inicializa la base de datos y crea la tabla si no existe en MySQL
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                cantidad INT NOT NULL DEFAULT 0,
                precio DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                categoria VARCHAR(100) NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente_nombre VARCHAR(255) NOT NULL,
                cliente_email VARCHAR(255) NOT NULL,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                total DECIMAL(10, 2) NOT NULL DEFAULT 0.00
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalles_pedido (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pedido_id INT NOT NULL,
                producto_id INT NOT NULL,
                cantidad INT NOT NULL,
                precio_unitario DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                rol VARCHAR(50) DEFAULT 'usuario'
            )
        ''')
        
        # Crear usuario admin por defecto si no existe
        cursor.execute("SELECT * FROM usuarios WHERE email = 'admin'")
        if not cursor.fetchone():
            from werkzeug.security import generate_password_hash
            hashed_admin = generate_password_hash('admin')
            cursor.execute('''
                INSERT INTO usuarios (nombre, email, password, rol) 
                VALUES (%s, %s, %s, %s)
            ''', ('Administrador', 'admin', hashed_admin, 'admin'))

        conn.commit()
        cursor.close()
        conn.close()

