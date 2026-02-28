import asyncio
import json
from datetime import datetime, timezone

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "general"):
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "general"):
        if channel in self.active_connections:
            self.active_connections[channel] = [
                ws for ws in self.active_connections[channel] if ws != websocket
            ]

    async def send_personal(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict, channel: str = "general"):
        if channel not in self.active_connections:
            return
        disconnected = []
        for ws in self.active_connections[channel]:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws, channel)

    async def broadcast_all(self, message: dict):
        for channel in list(self.active_connections.keys()):
            await self.broadcast(message, channel)


manager = ConnectionManager()


def create_event(event_type: str, data: dict) -> dict:
    return {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def notify_order_update(order_id: int, status: str):
    event = create_event("order_update", {"order_id": order_id, "status": status})
    await manager.broadcast(event, "orders")
    await manager.broadcast(event, "dashboard")


async def notify_stock_change(product_id: int, quantity: int, movement_type: str):
    event = create_event("stock_change", {
        "product_id": product_id,
        "quantity": quantity,
        "movement_type": movement_type,
    })
    await manager.broadcast(event, "stock")
    await manager.broadcast(event, "dashboard")


async def notify_picking_update(wave_id: int, status: str):
    event = create_event("picking_update", {"wave_id": wave_id, "status": status})
    await manager.broadcast(event, "picking")


async def notify_asn_update(asn_id: int, status: str):
    event = create_event("asn_update", {"asn_id": asn_id, "status": status})
    await manager.broadcast(event, "inbound")


async def notify_alert(alert_type: str, message: str, severity: str = "info"):
    event = create_event("alert", {
        "alert_type": alert_type,
        "message": message,
        "severity": severity,
    })
    await manager.broadcast_all(event)


async def notify_iot_alert(device_id: int, reading_type: str, value: float, unit: str):
    event = create_event("iot_alert", {
        "device_id": device_id,
        "reading_type": reading_type,
        "value": value,
        "unit": unit,
    })
    await manager.broadcast(event, "iot")
    await manager.broadcast(event, "dashboard")
