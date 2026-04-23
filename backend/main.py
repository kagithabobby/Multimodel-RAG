from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="Bilingual Technical Sensei API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    from services.retriever import retriever
    try:
        while True:
            data = await websocket.receive_text()
            # Simple wrapper to send incremental updates if model supports it,
            # or just send the final payload via WS.
            result = retriever.query(data)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        print("Client disconnected")

