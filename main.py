from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from chatbot import graph
from ml import predecir_subsidio  # Importar la función de predicción

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir modelo de datos
class DatosFormulario(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    telefono: str  # Cambiado de int a str
    tipoSubsidio: str  
    rsh: str
    situacionLaboral: str  # Corregido el nombre para coincidir con el JSON enviado
    ingresoMensual: int  
    montoAhorro: int  
    monedaAhorro: str  
    
    tieneAhorro: bool  
    tieneCi: bool  
    bienRaiz: bool  
    otroSubsidio: bool  # Agregado este campo que estaba en el JSON pero faltaba en la clase
    
    # Campos opcionales (se pueden ajustar según sea necesario)
    finalidadSubsidio: Optional[str] = None  
    subsidio: Optional[str] = None  
    tramos: Optional[int] = None  

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/datos")
def recibir_datos(datos: DatosFormulario):
    print("Datos recibidos:", datos)

    # Crear un diccionario con los datos relevantes para la predicción
    datos_prediccion = {
        'RSH': datos.rsh,
        'tiene_ahorro': int(datos.tieneAhorro),
        'moneda_uf': 1 if datos.monedaAhorro.lower() == "uf" else 0,
        'zona_interes': 1,  # Puedes asignar un valor basado en la lógica que uses
        'monto_ahorro': datos.montoAhorro,
        'ingreso_mensual': datos.ingresoMensual,
        'cant_integrante': 3  # Puedes cambiarlo según los datos
    }

    # Obtener predicción
    resultado = predecir_subsidio(datos_prediccion)

    return {"message": "Datos recibidos", "prediccion": resultado}


# Añade esto junto a tus otros modelos
class MensajeRequest(BaseModel):
    mensaje: str
    thread_id: str

# Modifica tu endpoint de mensajes así:
@app.post("/mensajes")
def procesar_mensaje(solicitud: MensajeRequest):
    try:
        config = {"configurable": {"thread_id": solicitud.thread_id}}
        
        result = graph.invoke(
            {"messages": [{"role": "user", "content": solicitud.mensaje}]},
            config
        )
        
        if result and "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            return {
                "respuesta": last_message.content,
                "thread_id": solicitud.thread_id
            }
            
        return {"error": "No se generó respuesta"}

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

