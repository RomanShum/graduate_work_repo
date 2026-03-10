# routes/ws_chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json

router = APIRouter(prefix="/ws", tags=["websocket"])


# Хранилище активных соединений
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
        print(f"Client connected to room {room_id}. Total: {len(self.active_connections[room_id])}")

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        print(f"Client disconnected from room {room_id}")

    async def broadcast(self, message: dict, room_id: str):
        if room_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)

            # Очищаем отключившиеся соединения
            for conn in disconnected:
                self.active_connections[room_id].discard(conn)


manager = ConnectionManager()


@router.websocket("/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_text()
            message = json.loads(data)

            # Добавляем информацию о комнате
            message["room_id"] = room_id

            # Отправляем всем в комнате
            await manager.broadcast(message, room_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
    except Exception as e:
        print(f"Error: {e}")
        manager.disconnect(websocket, room_id)