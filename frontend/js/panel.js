document.addEventListener("DOMContentLoaded", async function() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "login.html";
        return;
    }
    
    const contenedor = document.getElementById("contenedor-asignaturas");

    try {
        const response = await fetch("http://localhost:8001/asignaturas", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (response.ok) {
            const data = await response.json();
            const asignaturas = data.asignaturas;
            contenedor.innerHTML = "";

            if (asignaturas.length === 0) {
                contenedor.innerHTML = "<p>No hay asignaturas disponibles.</p>";
                return;
            }

            asignaturas.forEach(asignatura => {
                const tarjeta = document.createElement("div");
                tarjeta.innerHTML = `
                    <h3>${asignatura.nombre}</h3>
                    <p>Horas Totales: ${asignatura.horas_totales}</p>
                    <button onclick="verDetalles(${asignatura.id}, '${asignatura.horas_totales}')">Ver Notas y Faltas</button>
                `;
                contenedor.appendChild(tarjeta);
            });
        } else if (response.status === 401) {
            // Si el token caducó (pasaron los 30 min) o es falso
            alert('Tu sesión ha expirado. Vuelve a iniciar sesión.');
            localStorage.removeItem('token');
            window.location.href = 'index.html';
        } else {
            contenedor.innerHTML = '<p>Error al cargar las asignaturas.</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        contenedor.innerHTML = '<p>No se pudo conectar con el servidor.</p>';
    }

   const btnLogout = document.getElementById("logout");
    if (btnLogout) {
        btnLogout.addEventListener("click", function() {
            localStorage.removeItem("token");
            window.location.href = "login.html";
        });
    }
});