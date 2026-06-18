const formulario = document.getElementById('loginForm');

formulario.addEventListener('submit', async (event) => {
    event.preventDefault();

    // Preparamos los datos tal y como los espera FastAPI (OAuth2)
    const formData = new URLSearchParams();
    formData.append('username', document.getElementById('email').value);
    formData.append('password', document.getElementById('password').value);
    
    try {
        const response = await fetch('http://localhost:8001/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            // Guardamos el token en localStorage
            localStorage.setItem('token', data.access_token);
            // Redirigimos al usuario a la página de inicio
            alert('Inicio de sesión exitoso. Redirigiendo a la página de asignaturas...');
            window.location.href = 'panel_asignaturas.html';
        } else {
            alert('Correo o contraseña incorrectos. Por favor, inténtalo de nuevo.');
        }
    } catch (error) {
        console.error('Error al iniciar sesión:', error);
        alert('Ocurrió un error al iniciar sesión. Por favor, inténtalo de nuevo.');
    }
});