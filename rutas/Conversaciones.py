from fastapi import APIRouter, HTTPException, Depends
from configuracion.token import supabase
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# Definimos el modelo de la conversación
class Conversacion(BaseModel):
    user_id: int
    prompt: str
    messages: Optional[List[dict]] = []

router = APIRouter()

@router.post("/conversaciones/")
async def crear_conversacion(conversacion: Conversacion):
    try:
        # Insertar la nueva conversación en la tabla 'conversations'
        data = {
            "user_id": conversacion.user_id,
            "prompt": conversacion.prompt,
            "messages": conversacion.messages
        }
        
        # Intentar insertar los datos en la tabla de Supabase
        response = supabase.table('conversations').insert(data).execute()

        
        
        # Si la inserción es exitosa, retornar la respuesta
        return {"message": "Conversación creada exitosamente", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Función para verificar conversaciones
@router.get("/conversaciones/{user_id}")
async def verificar_conversaciones(user_id: int):
    try:
        # Verificar existencia del usuario
        user = supabase.table('users').select('*').eq('id', user_id).execute()
        if not user.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Verificar conversaciones
        conversaciones = supabase.table('conversations').select('id', count='exact').eq('user_id', user_id).execute()

        return {
            "tiene_conversaciones": conversaciones.count > 0,
            "total_conversaciones": conversaciones.count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    



