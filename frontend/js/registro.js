const form = document.getElementById('form-registro');

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const datosRegistro = {
        nombre: document.getElementById('nombre').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    try {
        // 2. Corregimos la ruta a /registro
        const response = await fetch('http://localhost:8001/registrar', {
            method: 'POST',
            headers: {
                // Le decimos al backend explícitamente que le mandamos un JSON
                'Content-Type': 'application/json'
            },
            // Convertimos nuestro objeto de JavaScript a una cadena de texto JSON
            body: JSON.stringify(datosRegistro)
        });

        if (response.ok) {
            alert('Registro exitoso. Ahora puedes iniciar sesión.');
            window.location.href = 'login.html';
        } else {
            alert('Error al registrarse. Por favor, inténtalo de nuevo.');
        }
    } catch (error) {
        console.error('Error al registrarse:', error);
        alert('Ocurrió un error al registrarse. Por favor, inténtalo de nuevo.');
    }
});