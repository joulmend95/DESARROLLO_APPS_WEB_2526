//Arreglo de lista de productos

const Productos = [
    {
        id: 1,
        nombre: "Producto 1",
        precio: 10.50,
        descripcion: "producto",
    },
    {
        id: 2,
        nombre: "Producto 2",
        precio: 20.00,
        descripcion: "producto",
    },
    {
        id: 3,
        nombre: "Producto 3",
        precio: 15.50,
        descripcion: "producto",
    },
    {
        id: 4,
        nombre: "Producto 4",
        precio: 40.00,
        descripcion: "producto",
    },
];

//Referencia del DOM            

const ul= document.getElementById("listaProductos");
const btnAgregar= document.getElementById("btnProducto");

//Renderizar la lista de productos

function renderProductos(){

    ul.innerHTML = "";
    Productos.forEach(producto => {
        const li = document.createElement("li");
        li.textContent = `${producto.nombre} - $${producto.precio} : ${producto.descripcion}`;
        ul.appendChild(li);

});
}

//Agregar nuevo producto
function agregarProducto(){
    const nuevoProducto = {
        id: Productos.length + 1,
        nombre: `Producto ${String.fromCharCode(65 + Productos.length)}`,
        precio: (Productos.length + 1) * 10.50,
        descripcion: `Descripcion ${String.fromCharCode(65 + Productos.length)}`,
    };
    Productos.push(nuevoProducto);
    renderProductos();
}

//Genera la lista

document.addEventListener("DOMContentLoaded", renderProductos);

//Eventos
btnAgregar.addEventListener("click", agregarProducto);

//Renderizado inicial
renderProductos();

