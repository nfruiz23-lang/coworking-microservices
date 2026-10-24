from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import httpx
import uvicorn

app = FastAPI(
    title="Orders Service",
    description="Servicio de gestión de órdenes de reserva con suscripción a eventos de catálogo",
    version="1.0.0"
)

# En Render o Docker Compose se sobreescribe con la URL del catalog-service
CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8001")
if CATALOG_SERVICE_URL and not CATALOG_SERVICE_URL.startswith("http://") and not CATALOG_SERVICE_URL.startswith("https://"):
    CATALOG_SERVICE_URL = f"https://{CATALOG_SERVICE_URL}"
if CATALOG_SERVICE_URL and "localhost" not in CATALOG_SERVICE_URL and "catalog-service:8001" not in CATALOG_SERVICE_URL and ".onrender.com" not in CATALOG_SERVICE_URL:
    CATALOG_SERVICE_URL = f"{CATALOG_SERVICE_URL}.onrender.com"

class Order(BaseModel):
    id: int
    space_id: int
    space_name: str
    user_email: str
    hours: int
    total_price: float
    status: str

class SpaceChangedEvent(BaseModel):
    event_type: str
    space_id: int
    space_name: str
    available: bool
    reason: Optional[str] = "Manual update"
    timestamp: str

# Bases de datos simuladas en memoria
ORDERS_DB = []
EVENTS_LOG = []

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "orders-service",
        "catalog_url": CATALOG_SERVICE_URL
    }

@app.get("/orders", response_model=List[Order])
def get_orders():
    return ORDERS_DB

@app.get("/events")
def get_events():
    """Devuelve el historial de eventos recibidos desde catalog-service"""
    return {
        "total_events_received": len(EVENTS_LOG),
        "events": EVENTS_LOG
    }

@app.post("/events/space-changed", status_code=200)
def receive_space_changed_event(event: SpaceChangedEvent):
    """
    CLASE 3 - Consumer / Suscriptor Event-Driven:
    Recibe eventos 'SpaceChanged' cuando catalog-service modifica la disponibilidad.
    """
    print(f"🔔 [EVENT RECEIVED] Evento recibido: Espacio '{event.space_name}' (ID: {event.space_id}) -> Disponible: {event.available}")
    
    event_record = {
        "received_at": datetime.utcnow().isoformat(),
        "event_data": event.dict()
    }
    EVENTS_LOG.append(event_record)

    # Si un espacio deja de estar disponible, actualizamos órdenes pendientes o registramos aviso
    if not event.available:
        print(f"⚠️ Aviso: El espacio {event.space_id} ya no está disponible para nuevas reservas.")

    return {
        "status": "Event processed successfully",
        "event_id": len(EVENTS_LOG)
    }

@app.post("/orders", response_model=Order, status_code=201)
async def create_order(
    space_id: int = Query(..., description="ID del espacio a reservar"),
    user_email: str = Query(..., description="Email del usuario que reserva"),
    hours: int = Query(..., ge=1, description="Cantidad de horas reservadas")
):
    target_url = f"{CATALOG_SERVICE_URL}/spaces/{space_id}"

    # Consulta HTTP al catalog-service con manejo de resiliencia
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(target_url)
    except httpx.RequestError:
        # LAB 4: Chaos Engineering - El catálogo está caído o inalcanzable
        raise HTTPException(
            status_code=503,
            detail="Catalog service unavailable"
        )

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Space with id {space_id} not found in catalog")

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error from catalog service: {response.text}"
        )

    space_data = response.json()

    # Validación de disponibilidad
    if not space_data.get("available", True):
        raise HTTPException(
            status_code=400,
            detail=f"Space '{space_data.get('name')}' is currently marked as unavailable for reservations"
        )

    # LAB 5: Chaos Engineering - Validación de contrato
    if "price_per_hour" not in space_data:
        raise HTTPException(
            status_code=500,
            detail="Contract violation: key 'price_per_hour' not found in catalog response"
        )

    price_per_hour = space_data["price_per_hour"]
    total_price = float(price_per_hour * hours)

    order = {
        "id": len(ORDERS_DB) + 1,
        "space_id": space_id,
        "space_name": space_data.get("name", "Espacio sin nombre"),
        "user_email": user_email,
        "hours": hours,
        "total_price": total_price,
        "status": "CONFIRMED"
    }

    ORDERS_DB.append(order)
    return order

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
