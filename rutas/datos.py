
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..ml import predecir_subsidio  # Importar la función de predicción

router = APIRouter()

# Modelo de datos
class DatosFormulario(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    telefono: str
    tipoSubsidio: str  
    rsh: str
    situacionLaboral: str
    ingresoMensual: int  
    montoAhorro: int  
    monedaAhorro: str  
    tieneAhorro: bool  
    tieneCi: bool  
    bienRaiz: bool  
    otroSubsidio: bool  
    finalidadSubsidio: Optional[str] = None  
    subsidio: Optional[str] = None  
    tramos: Optional[int] = None  

@router.post("/datos")
def recibir_datos(datos: DatosFormulario):
    print("Datos recibidos:", datos)
    datos_prediccion = {
        'RSH': datos.rsh,
        'tiene_ahorro': int(datos.tieneAhorro),
        'moneda_uf': 1 if datos.monedaAhorro.lower() == "uf" else 0,
        'zona_interes': 1,
        'monto_ahorro': datos.montoAhorro,
        'ingreso_mensual': datos.ingresoMensual,
        'cant_integrante': 3
    }
    resultado = predecir_subsidio(datos_prediccion)
    return {"message": "Datos recibidos", "prediccion": resultado}
