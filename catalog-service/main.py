from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import httpx
import uvicorn

app = FastAPI(
    title="Catalog Service",
    description="Servicio de catálogo de espacios de coworking con soporte de eventos",
    version="1.0.0"
)

ORDERS_SERVICE_URL = os.getenv("ORDERS_SERVICE_URL", "http://localhost:8002")
if ORDERS_SERVICE_URL and not ORDERS_SERVICE_URL.startswith("http://") and not ORDERS_SERVICE_URL.startswith("https://"):
    ORDERS_SERVICE_URL = f"https://{ORDERS_SERVICE_URL}"
if ORDERS_SERVICE_URL and "localhost" not in ORDERS_SERVICE_URL and "orders-service:8002" not in ORDERS_SERVICE_URL and ".onrender.com" not in ORDERS_SERVICE_URL:
    ORDERS_SERVICE_URL = f"{ORDERS_SERVICE_URL}.onrender.com"

class Space(BaseModel):
    id: int
    name: str
    capacity: int
    price_per_hour: float
    available: bool = True

class AvailabilityUpdate(BaseModel):
    available: bool
    reason: Optional[str] = "Manual update"

# Base de datos simulada en memoria
SPACES_DB = [
    {"id": 1, "name": "Hot Desk Flex", "capacity": 1, "price_per_hour": 15.0, "available": True},
    {"id": 2, "name": "Sala de Juntas Ejecutiva", "capacity": 8, "price_per_hour": 50.0, "available": True},
    {"id": 3, "name": "Oficina Privada Dual", "capacity": 2, "price_per_hour": 30.0, "available": True},
    {"id": 4, "name": "Cabina Insonorizada Call", "capacity": 1, "price_per_hour": 10.0, "available": True},
]

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "catalog-service",
        "orders_url": ORDERS_SERVICE_URL
    }

@app.get("/spaces", response_model=List[Space])
def get_spaces():
    return SPACES_DB

@app.get("/spaces/{space_id}", response_model=Space)
def get_space(space_id: int):
    for space in SPACES_DB:
        if space["id"] == space_id:
            return space
    raise HTTPException(status_code=404, detail="Space not found")

@app.post("/spaces/{space_id}/availability", response_model=Space)
async def update_availability(space_id: int, update: AvailabilityUpdate):
    """
    CLASE 3 - Event-Driven:
    Cuando cambia la disponibilidad, actualiza el estado y publica el evento 'SpaceChanged'
    a los servicios suscriptores (orders-service).
    """
    target_space = None
    for space in SPACES_DB:
        if space["id"] == space_id:
            space["available"] = update.available
            target_space = space
            break

    if not target_space:
        raise HTTPException(status_code=404, detail="Space not found")

    # Publicar evento SpaceChanged
    event_payload = {
        "event_type": "SpaceChanged",
        "space_id": space_id,
        "space_name": target_space["name"],
        "available": update.available,
        "reason": update.reason,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Despachar evento a orders-service
    subscriber_url = f"{ORDERS_SERVICE_URL}/events/space-changed"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.post(subscriber_url, json=event_payload)
            print(f"[EVENT PUBLISHED] Evento SpaceChanged enviado a {subscriber_url}")
    except Exception as exc:
        print(f"[EVENT NOTICE] No se pudo entregar a {subscriber_url} inmediatamente: {exc}")

    return target_space

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
