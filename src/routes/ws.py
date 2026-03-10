# routes/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
from datetime import datetime

router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_users: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, room_id: str, username: str):
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()

        self.active_connections[room_id].add(websocket)
        self.connection_users[websocket] = username

        print(f"✅ WebSocket подключен: {username} в комнате {room_id}")

        # Отправляем подтверждение
        await websocket.send_json({
            "type": "connection_established",
            "username": username,
            "room_id": room_id,
            "timestamp": datetime.now().isoformat()
        })

        # Уведомляем всех о новом пользователе
        await self.broadcast_to_room(
            room_id,
            {
                "type": "user_joined",
                "username": username,
                "timestamp": datetime.now().isoformat()
            },
            exclude=websocket
        )

    def disconnect(self, websocket: WebSocket, room_id: str):
        username = self.connection_users.get(websocket, "unknown")

        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

        if websocket in self.connection_users:
            del self.connection_users[websocket]

        print(f"❌ WebSocket отключен: {username} из комнаты {room_id}")

    async def broadcast_to_room(self, room_id: str, message: dict, exclude: WebSocket = None):
        """Отправить сообщение всем в комнате"""
        if room_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[room_id]:
                if exclude and connection == exclude:
                    continue
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Ошибка отправки: {e}")
                    disconnected.add(connection)

            # Очищаем отключившиеся соединения
            for conn in disconnected:
                self.active_connections[room_id].discard(conn)


manager = ConnectionManager()


@router.websocket("/{room_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str):
    await manager.connect(websocket, room_id, username)

    try:
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_text()
            message = json.loads(data)

            print(f"📨 Получено от {username}: {message.get('type')}")

            # Добавляем метаданные
            message["username"] = username
            message["timestamp"] = datetime.now().isoformat()

            # Обрабатываем разные типы сообщений
            message_type = message.get("type")

            if message_type == "chat":
                # Сообщение чата
                await manager.broadcast_to_room(room_id, {
                    "type": "chat",
                    "username": username,
                    "message": message.get("message", ""),
                    "timestamp": message["timestamp"]
                })

            elif message_type == "video":
                # Действие с видео
                await manager.broadcast_to_room(room_id, {
                    "type": "video",
                    "username": username,
                    "action": message.get("action"),
                    "time": message.get("time"),
                    "timestamp": message["timestamp"]
                })

            elif message_type == "ping":
                # Ответ на ping
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        # Уведомляем всех о выходе пользователя
        await manager.broadcast_to_room(
            room_id,
            {
                "type": "user_left",
                "username": username,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        print(f"Ошибка WebSocket: {e}")
        manager.disconnect(websocket, room_id)