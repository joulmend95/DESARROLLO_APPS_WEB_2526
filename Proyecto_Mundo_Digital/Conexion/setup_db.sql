-- Script para crear la tabla de productos en la base de datos MySQL

CREATE DATABASE IF NOT EXISTS mundo_digital_db;
USE mundo_digital_db;

CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    cantidad INT NOT NULL DEFAULT 0,
    precio DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    categoria VARCHAR(100) NOT NULL
);
