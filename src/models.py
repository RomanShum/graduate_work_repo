# models.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class User(BaseModel):
    name: str
    joined_at: str = None

class Room(BaseModel):
    id: str
    creator: str
    users: List[User] = []
    video_url: Optional[str] = None
    is_playing: bool = False
    current_time: float = 0
    created_at: str = None

class ChatMessage(BaseModel):
    username: str
    message: str
    timestamp: str = None

class VideoAction(BaseModel):
    username: str
    action: str  # 'play', 'pause', 'seek'
    time: float
    timestamp: str = None