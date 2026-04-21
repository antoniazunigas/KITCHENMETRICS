// Funcionario page JS: confirmaciones y solicitud de contraseña
function confirmarReserva() {
    return confirm("¿Estás seguro de realizar esta reserva para mañana? Una vez aceptado ya no hay cambios");
}

function solicitarPasswordRetiro() {
    // Pedimos la contraseña al usuario
    const password = prompt("Por favor, ingresa tu contraseña para confirmar el retiro del almuerzo:");
    
    // Si cancela o deja vacío, no se envía el formulario
    if (password === null || password === "") {
        return false; 
    }

    // Creamos un campo oculto en el formulario para enviar la contraseña al servidor
    const form = document.getElementById("form-retirar");
    const hiddenInput = document.createElement("input");
    hiddenInput.type = "hidden";
    hiddenInput.name = "password_confirmacion";
    hiddenInput.value = password;
    
    form.appendChild(hiddenInput);
    return true;
}
