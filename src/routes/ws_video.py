# routes/ws_video.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json

router = APIRouter(prefix="/ws/video", tags=["websocket-video"])


class VideoSyncManager:
    def __init__(self):
        self.connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()
        if room_id not in self.connections:
            self.connections[room_id] = {}
        self.connections[room_id][user_id] = websocket
        print(f"Video client connected to room {room_id}, user {user_id}")

    def disconnect(self, websocket: WebSocket, room_id: str, user_id: str):
        if room_id in self.connections and user_id in self.connections[room_id]:
            del self.connections[room_id][user_id]
            if not self.connections[room_id]:
                del self.connections[room_id]
        print(f"Video client disconnected from room {room_id}, user {user_id}")

    async def broadcast_video_state(self, room_id: str, message: dict, exclude_user: str = None):
        if room_id in self.connections:
            for user_id, conn in self.connections[room_id].items():
                if exclude_user and user_id == exclude_user:
                    continue
                try:
                    await conn.send_json(message)
                except:
                    pass


video_manager = VideoSyncManager()


@router.websocket("/{room_id}/{user_id}")
async def video_websocket(websocket: WebSocket, room_id: str, user_id: str):
    await video_manager.connect(websocket, room_id, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message["user_id"] = user_id

            # Отправляем состояние видео всем кроме отправителя
            await video_manager.broadcast_video_state(room_id, message, exclude_user=user_id)

    except WebSocketDisconnect:
        video_manager.disconnect(websocket, room_id, user_id)
    except Exception as e:
        print(f"Video sync error: {e}")
        video_manager.disconnect(websocket, room_id, user_id)