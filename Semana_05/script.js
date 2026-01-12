
// Traer los elementos del DOM
const inputurl = document.getElementById('urlimagen');
const btnAgregar = document.getElementById('btnAgregar');
const galeria = document.getElementById('galeria');

let imagenSeleccionada = null

// Función para agregar una nueva imagen a la galería

function agregarImagen() {
    const url = inputurl.value;
    if (url) {
        const nuevaImagen = document.createElement('img');
        nuevaImagen.src = url;
        nuevaImagen.classList.add('imagen-galeria');
        nuevaImagen.onclick = () => seleccionarImagen(nuevaImagen);
        galeria.appendChild(nuevaImagen);
        inputurl.value = '';
    }
}

// Función para seleccionar una imagen
function seleccionarImagen(imagen) {
    if (imagenSeleccionada) {
        imagenSeleccionada.classList.remove('seleccionada');
    }
    imagenSeleccionada = imagen;
    imagenSeleccionada.classList.add('seleccionada');
}

// Agregar event listener al botón
btnAgregar.addEventListener('click', agregarImagen);
