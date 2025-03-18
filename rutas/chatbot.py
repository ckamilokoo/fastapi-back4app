from fastapi import APIRouter , Depends
from pydantic import BaseModel
from chatbot.chatbot import graph 
from chatbot.paciente_psicologico import graph_paciente_psicologia
from rutas.acceso import get_current_user

router = APIRouter()

# Modelo para mensajes
class MensajeRequest(BaseModel):
    mensaje: str
    thread_id: str
    
    
class MensajeRequest_2(BaseModel):
    mensaje: str
    thread_id: str
    evento_traumatico:str
    informacion_paciente:str

@router.post("/mensajes")
def procesar_mensaje(solicitud: MensajeRequest,
    user: dict = Depends(get_current_user)):
    try:
        config = {"configurable": {"thread_id": solicitud.thread_id}}
        # Supongo que "graph" se importa desde algún módulo; asegúrate de importarlo
        
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
    
    
    
@router.post("/mensajes_psicologo")
def procesar_mensaje(solicitud: MensajeRequest_2):
    try:
        config = {"configurable": {"thread_id": solicitud.thread_id}}
        # Supongo que "graph" se importa desde algún módulo; asegúrate de importarlo
        
        result = graph_paciente_psicologia.invoke(
            {"respuesta": [{"role": "user", "content": solicitud.mensaje}],"evento_traumatico":solicitud.evento_traumatico,"informacion_paciente":solicitud.informacion_paciente},
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
