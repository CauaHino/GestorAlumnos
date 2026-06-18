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