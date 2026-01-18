//Referencias//

const form = document.getElementById('registroForm');
const nombre = document.getElementById('nombre');
const email = document.getElementById('email');
const password = document.getElementById('password');
const confirmarPassword = document.getElementById('confirmPassword');
const edad = document.getElementById('edad');

//Botones//
const botonRegistrar = document.getElementById('btnEnviar');
const mensajeExito = document.getElementById('mensajeExito');


//Errores//
const errorNombre = document.getElementById('nombreError');
const errorEmail = document.getElementById('emailError');
const errorPassword = document.getElementById('passwordError');
const errorConfirmarPassword = document.getElementById('confirmPasswordError');
const errorEdad = document.getElementById('edadError');

// ====== Expresiones regulares ====== //
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
// Mínimo 8 caracteres, una mayúscula, una minúscula y un número
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$/;

// ====== Funciones de validación ====== //
function setValid(input, errorElemento) {
    input.classList.remove("invalid");
    input.classList.add("valid");
    errorElemento.textContent = "";
}

function setInvalid(input, errorElemento, mensaje) {
    input.classList.remove("valid");
    input.classList.add("invalid");
    errorElemento.textContent = mensaje;
}

function clearState(input, errorElemento) {
    input.classList.remove("valid", "invalid");
    errorElemento.textContent = "";
}

// ====== Validaciones por campo ======
function validarNombre() {
  const value = nombre.value.trim();
  if (value.length === 0) {
    setInvalid(nombre, errorNombre, "El nombre es obligatorio.");
    return false;
  }
  if (value.length < 3) {
    setInvalid(nombre, errorNombre, "Mínimo 3 caracteres.");
    return false;
  }
  setValid(nombre, errorNombre);
  return true;
}

function validarEmail() {
  const value = email.value.trim();
  if (value.length === 0) {
    setInvalid(email, errorEmail, "El correo es obligatorio.");
    return false;
  }
  if (!emailRegex.test(value)) {
    setInvalid(email, errorEmail, "Formato de correo inválido. Ej:yo@gmail.com");
    return false;
  }
  setValid(email, errorEmail);
  return true;
}

function validarPassword() {
  const value = password.value;
  if (value.length === 0) {
    setInvalid(password, errorPassword, "La contraseña es obligatoria.");
    return false;
  }
  if (!passwordRegex.test(value)) {
    setInvalid(
      password,
      errorPassword,
      "Mín. 8 caracteres, una mayúscula, una minúscula y un número."
    );
    return false;
  }
  setValid(password, errorPassword);
  return true;
}

function validarConfirmPassword() {
  const value = confirmarPassword.value;
  if (value.length === 0) {
    setInvalid(confirmarPassword, errorConfirmarPassword, "Debes confirmar la contraseña.");
    return false;
  }
  if (value !== password.value) {
    setInvalid(confirmarPassword, errorConfirmarPassword, "Las contraseñas no coinciden.");
    return false;
  }
  setValid(confirmarPassword, errorConfirmarPassword);
  return true;
}

function validarEdad() {
  const value = edad.value.trim();
  if (value.length === 0) {
    setInvalid(edad, errorEdad, "La edad es obligatoria.");
    return false;
  }
  const n = Number(value);
  if (Number.isNaN(n)) {
    setInvalid(edad, errorEdad, "Ingresa un número válido.");
    return false;
  }
  if (n < 18) {
    setInvalid(edad, errorEdad, "Debes ser mayor o igual a 18 años.");
    return false;
  }
  setValid(edad, errorEdad);
  return true;
}

function actualizarEstadoBoton() {
  const ok =
    validarNombre() &&
    validarEmail() &&
    validarPassword() &&
    validarConfirmPassword() &&
    validarEdad();

  botonRegistrar.disabled = !ok;
  return ok;
}

// ====== Eventos en tiempo real ======
nombre.addEventListener("input", () => {
  validarNombre();
  actualizarEstadoBoton();
});

email.addEventListener("input", () => {
  validarEmail();
  actualizarEstadoBoton();
});

password.addEventListener("input", () => {
  validarPassword();
  // si cambia la contraseña, revalidar confirmación
  if (confirmarPassword.value.length > 0) validarConfirmPassword();
  actualizarEstadoBoton();
});

confirmarPassword.addEventListener("input", () => {
  validarConfirmPassword();
  actualizarEstadoBoton();
});

edad.addEventListener("input", () => {
  validarEdad();
  actualizarEstadoBoton();
});

// ====== Envío del formulario ======
form.addEventListener("submit", (e) => {
  e.preventDefault();

  mensajeExito.textContent = "";
  const ok = actualizarEstadoBoton();

  if (ok) {
    alert("✅ Formulario validado correctamente. ¡Registro exitoso!");
    mensajeExito.textContent = "✅ Validación exitosa. Puedes enviar tus datos con seguridad.";
    mensajeExito.style.display = "block";
    form.reset();
    botonRegistrar.disabled = true;

    // limpiar estilos/errores tras reset manual
    [nombre, email, password, confirmarPassword, edad].forEach((inp) => inp.classList.remove("valid", "invalid"));
    [errorNombre, errorEmail, errorPassword, errorConfirmarPassword, errorEdad].forEach((el) => (el.textContent = ""));
  }
});

// ====== Reset ======
form.addEventListener("reset", () => {
  mensajeExito.textContent = "";
  mensajeExito.style.display = "none";
  botonRegistrar.disabled = true;

  setTimeout(() => {
    [nombre, email, password, confirmarPassword, edad].forEach((inp) => inp.classList.remove("valid", "invalid"));
    [errorNombre, errorEmail, errorPassword, errorConfirmarPassword, errorEdad].forEach((el) => (el.textContent = ""));
  }, 0);
});