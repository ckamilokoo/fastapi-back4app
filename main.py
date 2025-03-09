from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar e incluir los routers
from rutas import datos, chatbot, stream ,acceso

print(chatbot)
app.include_router(datos.router)
app.include_router(chatbot.router)
app.include_router(stream.router)
app.include_router(acceso.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

