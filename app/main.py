from datetime import date

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Importamos nuestros propios módulos
from . import models, auth, database

# Creamos las tablas en la base de datos (si no existen ya)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title = "GestorAlumno", description = "API para gestionar alumnos, asignaturas, notas y faltas")

# Esto le dice a la API: "Permite que cualquier página web local hable conmigo"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción aquí pondrías la URL de tu web real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AlumnoCreate(BaseModel):
    nombre: str
    email: str
    password: str

class NotaCreate(BaseModel):
    asignatura_id: int
    nombre_examen: str
    valor: float
    peso_porcentaje: int

class FaltaCreate(BaseModel):
    fecha: date  # Formato "YYYY-MM-DD"
    justificada: bool
    horas_perdidas: int

def obtener_alumno(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    """Esta función intercepta las peticiones, valida el token y busca al usuario en SQLite."""
    # Verificamos el token y obtenemos el email del alumno
    email = auth.verificar_token_acceso(token)
        
    # Buscamos al alumno por email
    alumno = db.query(models.Alumno).filter(models.Alumno.email == email).first()
        
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
        
    return alumno


@app.post("/registrar")
def registrar_alumno(alumno: AlumnoCreate, db: Session = Depends(get_db)):
    # Verificamos si el email ya está registrado
    db_alumno = db.query(models.Alumno).filter(models.Alumno.email == alumno.email).first()
    if db_alumno:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Creamos un nuevo alumno con la contraseña hasheada
    hashed_password = auth.obtener_password_hash(alumno.password)
    nuevo_alumno = models.Alumno(nombre=alumno.nombre, email=alumno.email, password_hashed=hashed_password)
    
    db.add(nuevo_alumno)
    db.commit()
    db.refresh(nuevo_alumno)

    # ==========================================
    # 3. AUTO-GENERAR ASIGNATURAS FIJAS
    # ==========================================
    modulos_dam = [
        {"nombre": "Acceso a Datos", "horas_totales": 233},
        {"nombre": "Desarrollo de Interfaces", "horas_totales": 233},
        {"nombre": "Programación Multimedia y Dispositivos Móviles", "horas_totales": 158},
        {"nombre": "Programación de Servicios y Procesos", "horas_totales": 84},
        {"nombre": "Sistemas de Gestión Empresarial", "horas_totales": 158},
        {"nombre": "Itinerario personal para empleabilidad II", "horas_totales": 60},
        {"nombre": "Programación web asíncrona mediante frameworks", "horas_totales": 80},
        {"nombre": "Proyecto Intermodular", "horas_totales": 55}
    ]
    
    for modulo in modulos_dam:
        nueva_asignatura = models.Asignatura(
            nombre=modulo["nombre"],
            horas_totales=modulo["horas_totales"],
            alumno_id=nuevo_alumno.id
        )
        db.add(nueva_asignatura)
    
    db.commit()

    return {"mensaje": "Alumno registrado exitosamente", "alumno_id": nuevo_alumno.id}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Buscamos al alumno por email
    alumno = db.query(models.Alumno).filter(models.Alumno.email == form_data.username).first()
    
    if not alumno or not auth.verificar_password(form_data.password, alumno.password_hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Creamos el token de acceso
    token = auth.crear_token_acceso(data={"sub": alumno.email})
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/asignaturas")
def obtener_asignaturas(alumno: models.Alumno = Depends(obtener_alumno)):
    
    return {"asignaturas": [{"id": asignatura.id, "nombre": asignatura.nombre, "horas_totales": asignatura.horas_totales} for asignatura in alumno.asignaturas]}


@app.post("/asignaturas/{asignatura_id}/notas")
def agregar_nota(asignatura_id: int, nota: NotaCreate, usuario_actual: models.Alumno = Depends(obtener_alumno), db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    # 1. Comprobamos que la asignatura existe y pertenece a este alumno
    asignatura = db.query(models.Asignatura).filter(
        models.Asignatura.id == asignatura_id, 
        models.Asignatura.alumno_id == usuario_actual.id
    ).first()
    
    if not asignatura:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada o no tienes permisos")
    
    # 2. Creamos la nueva nota
    nueva_nota = models.Nota(
        asignatura_id=asignatura_id,
        nombre_examen=nota.nombre_examen,
        valor=nota.valor,
        peso_porcentaje=nota.peso_porcentaje
    )
    db.add(nueva_nota)
    db.commit()

    return {"mensaje": "Nota agregada exitosamente"}

@app.get("/asignaturas/{asignatura_id}/detalles")
def obtener_detalles_asignatura(asignatura_id: int, usuario_actual: models.Alumno = Depends(obtener_alumno)):
    # 1. Comprobamos que la asignatura existe y pertenece a este alumno
    asignatura = next((a for a in usuario_actual.asignaturas if a.id == asignatura_id), None)
    
    if not asignatura:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada o no tienes permisos")
    
    # 2. Preparamos los detalles de la asignatura
    detalles = {
        "nombre": asignatura.nombre,
        "horas_totales": asignatura.horas_totales,
        "notas": [{"nombre_examen": n.nombre_examen, "valor": n.valor, "peso_porcentaje": n.peso_porcentaje} for n in asignatura.notas],
        "faltas": [{"fecha": f.fecha.isoformat(), "horas": f.horas_perdidas, "justificada": bool(f.justificada)} for f in asignatura.faltas]
    }
    
    return detalles

@app.post("/asignaturas/{asignatura_id}/faltas")
def agregar_falta(asignatura_id: int, falta: FaltaCreate, usuario_actual: models.Alumno = Depends(obtener_alumno), db: Session = Depends(get_db)):
    # 1. Comprobamos que la asignatura existe y pertenece a este alumno
    asignatura = next((a for a in usuario_actual.asignaturas if a.id == asignatura_id), None)
    
    if not asignatura:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada o no tienes permisos")
    
    # 2. Creamos la nueva falta
    nueva_falta = models.Falta(
        fecha=falta.fecha,
        horas_perdidas=falta.horas_perdidas,
        justificada=False,  # Por defecto la ponemos como injustificada
        asignatura_id=asignatura_id
    )
    
    db.add(nueva_falta)
    db.commit()

    return {"mensaje": "Falta agregada exitosamente"}
                  
