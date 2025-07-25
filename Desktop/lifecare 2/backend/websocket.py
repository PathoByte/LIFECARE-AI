from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user: {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user: {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[user_id].remove(conn)
    
    async def broadcast_to_all(self, message: dict):
        for user_id, connections in self.active_connections.items():
            disconnected = []
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                connections.remove(conn)

manager = ConnectionManager()

async def handle_websocket(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            elif message.get("type") == "subscribe":
                # Handle subscription to specific data streams
                await websocket.send_text(json.dumps({
                    "type": "subscribed",
                    "channel": message.get("channel"),
                    "timestamp": datetime.utcnow().isoformat()
                }))
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)

async def send_health_update(user_id: str, health_data: dict):
    """Send real-time health data update to user"""
    message = {
        "type": "health_update",
        "data": health_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.send_personal_message(message, user_id)

async def send_alert(user_id: str, alert_data: dict):
    """Send real-time alert to user"""
    message = {
        "type": "alert",
        "data": alert_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.send_personal_message(message, user_id)