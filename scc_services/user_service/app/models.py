# app/models.py

from pydantic import BaseModel

# Modelo de datos que esperamos recibir del frontend
# clase para el registro de un usuario
class RegistroUsuario(BaseModel):
    region: str
    localidad: str
    username: str
    rol: str
    createdBy: str # Usuario que realiza el registro

# clase para la actualización de un usuario
class ActualizarUsuario(BaseModel):
    # Ya no se requiere 'id_location' ya que el SP la maneja por nombre
    id_region: int            # ID de la región seleccionada
    location_name: str        # Nuevo nombre de la localidad
    id_rol: str               # ID del nuevo rol
    is_active: bool           # Estado de activación
    changedBy: str            # Usuario que hace el cambio