from fastapi import APIRouter, HTTPException, Depends
from configuracion.token import supabase
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# Definimos el modelo de la conversación
class Conversacion(BaseModel):
    username: str
    prompt: str
    messages: Optional[List[dict]] = []
    
class eliminar_conversacion(BaseModel):
    username: str
    id_conversacion: str

router = APIRouter()

@router.post("/conversaciones/")
async def crear_conversacion(conversacion: Conversacion):
    try:
        verificar_usuario = supabase.table('users').select('*').eq('username', conversacion.username).execute()
        #print(verificar_usuario.data[0]['id'])
        if verificar_usuario.data:
            # Insertar la nueva conversación en la tabla 'conversations'
            data = {
                "user_id": verificar_usuario.data[0]['id'],
                "prompt": conversacion.prompt,
                "messages": conversacion.messages
            }
            
            # Intentar insertar los datos en la tabla de Supabase
            response = supabase.table('conversations').insert(data).execute()

            
            
            # Si la inserción es exitosa, retornar la respuesta
            return {"message": "Conversación creada exitosamente", "data": response.data}
        
        else:
            return {"message": "Usuario no encontrado"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/conversaciones_eliminar/")
async def crear_conversacion(informacion : eliminar_conversacion):
    try:
        #print(informacion.id_conversacion)
        verificar_usuario = supabase.table('users').select('*').eq('username', informacion.username).execute()
        #print(verificar_usuario.data[0]['id'])
        if verificar_usuario.data:
            # Insertar la nueva conversación en la tabla 'conversations'
            
            response = (supabase.table("conversations").delete().eq("id", informacion.id_conversacion).execute())

            if response.data:
            # Intentar insertar los datos en la tabla de Supabase
            #response = supabase.table('conversations').insert(data).execute()

            
            
            # Si la inserción es exitosa, retornar la respuesta
                return {"message": "Conversación eliminada exitosamente"}
            else:
                return {"message": "ID incorrecto de conversacion"}
            
                
        
        else:
            return {"message": "Usuario no encontrado"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Función para verificar conversaciones
@router.get("/conversaciones/{username}")
async def verificar_conversaciones(username:str):
    try:
        verificar_usuario = supabase.table('users').select('*').eq('username', username).execute()
        #print(verificar_usuario.data[0]['id'])
        if verificar_usuario.data:
            # Verificar existencia del usuario
            print("1")
            user = supabase.table('users').select('*').eq('id', verificar_usuario.data[0]['id']).execute()
            if not user.data:
                print("2")
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            print("3")
            # Verificar conversaciones
            conversaciones = supabase.table('conversations').select('id' , 'prompt', 'messages', count='exact').eq('user_id', verificar_usuario.data[0]['id']).execute()
            print(conversaciones.data)
            #primero se crear una variable para guardar los id
            prompts = []
            #despues se recorre el valor de data dentro de conversaciones cada uno con un nombre item
            for item in conversaciones.data:
                #se utiliza la variable de los ids para agregar cada valor de id dentro de item.
                prompts.append(item)
                
                    

            print("IDs obtenidos:", prompts)
            return {
                "tiene_conversaciones": prompts,
            }
        else:
            return {"message": "Usuario no encontrado"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    



