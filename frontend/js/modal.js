async function verDetalles(idAsignatura, horasTotales) {
    const token = localStorage.getItem("token");
    
    const modal = document.getElementById("mi-modal");
    const listaNotas = document.getElementById("lista-notas");
    const listaFaltas = document.getElementById("lista-faltas");

    modal.style.display = "block";
    listaNotas.innerHTML = "<li>Cargando notas...</li>";
    listaFaltas.innerHTML = "<li>Cargando faltas...</li>";

    try {
        const response = await fetch(`http://localhost:8001/asignaturas/${idAsignatura}/detalles`, {
            headers: { 
                "Authorization": `Bearer ${token}` 
            }
        });

        if (response.ok) {
            const detalles = await response.json();
            
            listaNotas.innerHTML = "";
            listaFaltas.innerHTML = "";

            // Rellenamos las notas y ponemos el botón de abrir el 2º modal
            listaNotas.innerHTML = `<button onclick="abrirModalNota(${idAsignatura}, ${horasTotales})" style="margin-bottom: 10px; cursor:pointer;">+ Añadir Nota</button><br>`;
            
            if (detalles.notas.length === 0) {
                listaNotas.innerHTML += "<li>No hay notas registradas.</li>";
            } else {
                detalles.notas.forEach(nota => {
                    listaNotas.innerHTML += `<li>${nota.nombre_examen}: <strong>${nota.valor}</strong> (${nota.peso_porcentaje}%)</li>`;
                });
            }

            let sumaHorasFalta = 0;
            
            detalles.faltas.forEach(falta => {
                sumaHorasFalta += falta.horas;
            });

            // Calculamos el límite estricto (25% del total del módulo)
            const limiteFaltas = horasTotales * 0.25;
            
            // Calculamos qué porcentaje del LÍMITE has consumido ya
            let porcentajeConsumido = (sumaHorasFalta / limiteFaltas) * 100;
            
            // Evitamos que la barra se salga de la pantalla si te pasas del 100%
            if (porcentajeConsumido > 100) porcentajeConsumido = 100; 

            // Decidimos el color (Verde < 50%, Naranja > 50%, Rojo > 80%)
            let colorClase = "progreso-verde";
            if (porcentajeConsumido >= 80) {
                colorClase = "progreso-rojo";
            } else if (porcentajeConsumido >= 50) {
                colorClase = "progreso-naranja";
            }

            // Dibujamos la barra y el texto informativo
            listaFaltas.innerHTML = `
                <div class="progreso-texto">
                    Límite (25%): Has consumido <strong>${sumaHorasFalta}h</strong> de las <strong>${limiteFaltas}h</strong> permitidas.
                </div>
                <div class="progreso-contenedor">
                    <div class="progreso-relleno ${colorClase}" style="width: ${porcentajeConsumido}%"></div>
                </div>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 10px 0;">
            `;

            // Debajo de la barra, pintamos la lista normal de los días que faltaste
            if (detalles.faltas.length === 0) {
                listaFaltas.innerHTML += "<li>No tienes faltas registradas. ¡Sigue así!</li>";
            } else {
                detalles.faltas.forEach(falta => {
                    listaFaltas.innerHTML += `<li>${falta.fecha}: ${falta.horas} horas perdidas</li>`;
                });
            }

        } else {
            listaNotas.innerHTML = "<li>Error al cargar los datos.</li>";
            listaFaltas.innerHTML = "";
        }
    } catch (error) {
        console.error("Error cargando detalles:", error);
    }

    // ==========================================
    // LÓGICA PARA AÑADIR UNA NUEVA FALTA
    // ==========================================
    const formFalta = document.getElementById("form-nueva-falta");
    
    // Usamos onsubmit en lugar de addEventListener para que no se dupliquen 
    // los envíos si abres y cierras el modal varias veces
    formFalta.onsubmit = async function(event) {
        event.preventDefault();

        const fecha = document.getElementById("input-fecha-falta").value;
        const horas = parseInt(document.getElementById("input-horas-falta").value);

        const nuevaFalta = {
            fecha: fecha,
            horas_perdidas: horas,
            justificada: false
        };

        try {
            const respuestaPost = await fetch(`http://localhost:8001/asignaturas/${idAsignatura}/faltas`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json" // Enviamos JSON puro
                },
                body: JSON.stringify(nuevaFalta)
            });

            if (respuestaPost.ok) {
                // Si se guardó bien, limpiamos el formulario...
                formFalta.reset();
                // volvemos a llamar a verDetalles para que la barra 
                // se recalcule con las nuevas horas y haga la animación
                verDetalles(idAsignatura, horasTotales);
            } else {
                alert("Hubo un problema al guardar la falta.");
            }
        } catch (error) {
            console.error("Error al enviar la falta:", error);
        }
    };

    const cerrarModal = document.getElementById("btn-cerrar-modal");
    cerrarModal.addEventListener("click", () => {
    const modal = document.getElementById("mi-modal");
    modal.style.display = "none";
});
}

// ==========================================
// LÓGICA DEL SEGUNDO MODAL (AÑADIR NOTA)
// ==========================================
const modalNota = document.getElementById("modal-nueva-nota");
const btnCerrarNota = document.getElementById("btn-cerrar-modal-nota");
const formNota = document.getElementById("form-nueva-nota");

// Variables para recordar a qué asignatura le estamos poniendo la nota
let idAsigActual = null;
let horasTotalesActual = null;

// Función para abrir el segundo modal
function abrirModalNota(idAsignatura, horasTotales) {
    idAsigActual = idAsignatura;
    horasTotalesActual = horasTotales;
    modalNota.style.display = "block";
}

// Cerrar el segundo modal en la X
btnCerrarNota.onclick = function() {
    modalNota.style.display = "none";
}

// Envío del formulario del segundo modal
formNota.onsubmit = async function(event) {
    event.preventDefault(); 

    const token = localStorage.getItem("token");
    const nuevaNota = {
        asignatura_id: idAsigActual,
        nombre_examen: document.getElementById("input-nombre-examen").value,
        valor: parseFloat(document.getElementById("input-valor-nota").value),
        peso_porcentaje: parseInt(document.getElementById("input-peso-nota").value)
    };

    try {
        const respuesta = await fetch(`http://localhost:8001/asignaturas/${idAsigActual}/notas`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(nuevaNota)
        });

        if (respuesta.ok) {
            formNota.reset();
            modalNota.style.display = "none"; // Escondemos el segundo modal
            verDetalles(idAsigActual, horasTotalesActual); // Refrescamos el primer modal para ver la nota nueva
        } else {
            alert("Error al guardar la nota.");
        }
    } catch (error) {
        console.error("Error:", error);
    }
};

// Cerrar cualquier modal si se hace clic fuera de la caja blanca
window.onclick = function(event) {
    const modalDetalles = document.getElementById("mi-modal");
    if (event.target === modalDetalles) {
        modalDetalles.style.display = "none";
    }
    if (event.target === modalNota) {
        modalNota.style.display = "none";
    }
}

