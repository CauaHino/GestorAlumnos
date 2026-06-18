from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from .database import Base

class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    email = Column(String, unique=True, index=True)
    # CRUCIAL: Nunca guardamos la contraseña en texto plano, guardamos su "hash" cifrado
    password_hashed = Column(String) 

    # Relación: Un alumno tiene muchas asignaturas
    asignaturas = relationship("Asignatura", back_populates="alumno")


class Asignatura(Base):
    __tablename__ = "asignaturas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    horas_totales = Column(Integer)

    # NUEVO: Clave foránea para saber de quién es esta asignatura
    alumno_id = Column(Integer, ForeignKey("alumnos.id"))
    
    # Relaciones
    alumno = relationship("Alumno", back_populates="asignaturas")
    notas = relationship("Nota", back_populates="asignatura")
    faltas = relationship("Falta", back_populates="asignatura")
class Nota(Base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, index=True)
    nombre_examen = Column(String) # Ej: "Examen Trimestre 1" o "Proyecto Final"
    valor = Column(Float) # Tu nota del 0 al 10
    peso_porcentaje = Column(Integer) # Cuánto vale para la media (ej: 40 para un 40%)
    
    # Clave foránea que conecta con la tabla de asignaturas
    asignatura_id = Column(Integer, ForeignKey("asignaturas.id"))
    
    # Relación inversa
    asignatura = relationship("Asignatura", back_populates="notas")

class Falta(Base):
    __tablename__ = "faltas"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date)
    horas_perdidas = Column(Integer) # Cuántas horas de clase te saltaste ese día
    justificada = Column(Integer, default=0) # 0 para no, 1 para sí (SQLite usa enteros para booleanos)

    # Clave foránea
    asignatura_id = Column(Integer, ForeignKey("asignaturas.id"))

    # Relación inversa
    asignatura = relationship("Asignatura", back_populates="faltas")