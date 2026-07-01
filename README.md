# GestorAlumno - Sistema de Control Académico

Una aplicación web moderna e intuitiva diseñada para que los estudiantes de Ciclos Formativos (FP) puedan autogestionar su progreso académico en tiempo real. Permite realizar un seguimiento exhaustivo de las calificaciones ponderadas y controlar de forma visual el límite crítico de faltas de asistencia para no perder la evaluación continua.

---

## Características Principales

### Backend (FastAPI + SQLAlchemy)
* **Arquitectura RESTful:** Endpoints limpios y estructurados para operaciones CRUD de alumnos, asignaturas, notas y faltas.
* **Seguridad Robusta:** Autenticación de usuarios mediante tokens **JWT (JSON Web Tokens)** con hashing de contraseñas mediante `passlib`.
* **Persistencia de Datos:** Integración con **SQLite** mediante el ORM SQLAlchemy, optimizando la gestión de conexiones mediante inyección de dependencias (`Depends`).
* **Automatización del Currículo:** Al registrarse un nuevo alumno, el sistema genera automáticamente la carga horaria oficial del ciclo formativo de DAM.

### Frontend (Vanilla Tech Stack & Premium UI)
* **Estilo Dark Mode:** Interfaz minimalista inspirada en los patrones de diseño de Vercel y Apple, utilizando una paleta de colores Zinc, degradados radiales sutiles y efectos de *Glassmorphism* (cristal esmerilado).
* **Experiencia SPA (Single Page Application):** Uso intensivo de la API Fetch asíncrona y manipulación dinámica del DOM para realizar acciones sin recargar la página.
* **Modales de Acción Avanzados:** Ventanas emergentes en capas que separan la visualización de detalles del ingreso de nuevos registros de evaluación.
* **Control de Asistencia UX:** Barra de progreso dinámica que calcula el **límite estricto del 25%** de faltas permitidas por asignatura, cambiando de color (Verde → Naranja → Rojo) según el nivel de riesgo del estudiante.
* **Cálculo de Nota Media Ponderada:** Algoritmo en JavaScript que computa en tiempo real el promedio real basándose en el peso porcentual de cada examen.

---

## Tecnologías Utilizadas

* **Backend:** Python 3.14+, FastAPI, SQLAlchemy, Pydantic, Uvicorn.
* **Frontend:** HTML5, CSS3 (Flexbox/Grid, Variables Nativas), JavaScript Asíncrono (ES6+).
* **Base de Datos:** SQLite.

---

## Instalación y Configuración

### Prerrequisitos
Asegúrate de tener instalado Python en tu sistema operativo (probado y optimizado en entornos Linux/Fedora).

### 1. Clonar el repositorio e ingresar
```bash
git clone [https://github.com/tu-usuario/GestorAlumno.git](https://github.com/tu-usuario/GestorAlumno.git)
cd GestorAlumno