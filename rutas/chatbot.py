from fastapi import APIRouter
from pydantic import BaseModel
from ..chatbot.chatbot import graph

router = APIRouter()

# Modelo para mensajes
class MensajeRequest(BaseModel):
    mensaje: str
    thread_id: str

@router.post("/mensajes")
def procesar_mensaje(solicitud: MensajeRequest):
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
