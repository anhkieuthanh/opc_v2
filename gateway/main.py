import asyncio
import json
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from agents.base.queue import RabbitMQClient
from gateway.ws import ConnectionManager
from shared.message import MessageType, OPCMessage, Payload

load_dotenv()

manager = ConnectionManager()
queue_client = RabbitMQClient(os.environ["RABBITMQ_URL"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    await queue_client.connect()
    asyncio.create_task(_listen_gateway_queue())
    yield
    await queue_client.close()


app = FastAPI(title="OPC Gateway", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _listen_gateway_queue() -> None:
    async def on_message(msg: OPCMessage) -> None:
        await manager.broadcast(msg.to_dict())

    await queue_client.consume("gateway", on_message)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            msg = OPCMessage(
                from_agent="user",
                to="ceo",
                type=MessageType.TASK,
                payload=Payload(content=data["content"]),
            )
            await queue_client.publish("ceo", msg)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/agents/status")
async def agents_status() -> dict:
    return {
        "agents": [
            {"id": "ceo", "status": "active"},
            {"id": "marketing", "status": "active"},
            {"id": "sales", "status": "active"},
            {"id": "support", "status": "active"},
        ]
    }


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
