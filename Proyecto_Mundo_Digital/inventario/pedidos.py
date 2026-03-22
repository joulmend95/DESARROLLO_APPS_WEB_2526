import json
import csv
import os
from Conexion.conexion import get_db_connection

def crear_pedido(cliente_nombre, cliente_email, total, carrito_items):
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    # Insertar pedido
    cursor.execute('INSERT INTO pedidos (cliente_nombre, cliente_email, total) VALUES (%s, %s, %s)', 
                   (cliente_nombre, cliente_email, total))
    pedido_id = cursor.lastrowid
    
    # Insertar detalles
    for item in carrito_items.values():
        cursor.execute('INSERT INTO detalles_pedido (pedido_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)',
                       (pedido_id, item['id'], item['cantidad'], item['precio']))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Sincronizar con TXT, JSON, CSV
    sincronizar_pedidos()
    return pedido_id

def obtener_pedidos():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM pedidos ORDER BY fecha DESC')
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return pedidos

def obtener_detalles_pedido(pedido_id):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT dp.*, p.nombre 
        FROM detalles_pedido dp
        JOIN productos p ON dp.producto_id = p.id
        WHERE dp.pedido_id = %s
    ''', (pedido_id,))
    detalles = cursor.fetchall()
    cursor.close()
    conn.close()
    return detalles

def obtener_pedido_con_detalles(pedido_id):
    conn = get_db_connection()
    if not conn:
        return None, []
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM pedidos WHERE id = %s', (pedido_id,))
    pedido = cursor.fetchone()
    
    cursor.execute('''
        SELECT dp.*, p.nombre 
        FROM detalles_pedido dp
        LEFT JOIN productos p ON dp.producto_id = p.id
        WHERE dp.pedido_id = %s
    ''', (pedido_id,))
    detalles = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return pedido, detalles

def sincronizar_pedidos():
    pedidos = obtener_pedidos()
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Convertir datetimes a strings para JSON
    for p in pedidos:
        if 'fecha' in p and p['fecha']:
            p['fecha'] = str(p['fecha'])
        if 'total' in p:
            p['total'] = float(p['total'])
            
    # JSON
    with open(os.path.join(data_dir, 'pedidos.json'), 'w', encoding='utf-8') as f:
        json.dump(pedidos, f, indent=4)
        
    # CSV
    if pedidos:
        with open(os.path.join(data_dir, 'pedidos.csv'), 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=pedidos[0].keys())
            writer.writeheader()
            writer.writerows(pedidos)
            
    # TXT
    with open(os.path.join(data_dir, 'pedidos.txt'), 'w', encoding='utf-8') as f:
        for p in pedidos:
            f.write(f"Pedido {p['id']} - {p['cliente_nombre']} ({p['fecha']}) - Total: \n")

