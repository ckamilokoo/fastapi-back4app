from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio

router = APIRouter()

async def data_generator():
    for i in range(10):
        yield f"Mensaje {i}\n"
        await asyncio.sleep(1)

@router.get("/stream", response_class=StreamingResponse)
async def stream_endpoint():
    return StreamingResponse(data_generator(), media_type="text/plain")
