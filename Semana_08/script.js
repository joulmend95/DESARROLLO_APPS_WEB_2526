
// Esperar a que cargue la página
document.addEventListener('DOMContentLoaded', function() {
    
    // Botón de alerta
    const btnAlerta = document.getElementById('btnAlerta');
    btnAlerta.addEventListener('click', function() {
        alert('¡Bienvenido a nuestra tienda!');
    });

    // Validación del formulario
    const formulario = document.getElementById('contactForm');
    const nombre = document.getElementById('nombre');
    const email = document.getElementById('email');
    const mensaje = document.getElementById('mensaje');

    formulario.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Limpiar validaciones previas
        nombre.classList.remove('is-invalid', 'is-valid');
        email.classList.remove('is-invalid', 'is-valid');
        mensaje.classList.remove('is-invalid', 'is-valid');
        
        let valido = true;

        // Validar nombre
        if (nombre.value.trim() === '') {
            nombre.classList.add('is-invalid');
            valido = false;
        } else {
            nombre.classList.add('is-valid');
        }

        // Validar email
        if (email.value.trim() === '' || !email.value.includes('@')) {
            email.classList.add('is-invalid');
            valido = false;
        } else {
            email.classList.add('is-valid');
        }

        // Validar mensaje
        if (mensaje.value.trim() === '') {
            mensaje.classList.add('is-invalid');
            valido = false;
        } else {
            mensaje.classList.add('is-valid');
        }

        // Si todo es válido
        if (valido) {
            alert('¡Mensaje enviado con éxito!');
            formulario.reset();
            nombre.classList.remove('is-valid');
            email.classList.remove('is-valid');
            mensaje.classList.remove('is-valid');
        }
    });
    
});