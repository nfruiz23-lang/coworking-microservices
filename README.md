# Workshop de Microservicios & Chaos Engineering: Coworking Spaces

Este repositorio contiene la solución completa, explicada paso a paso, para los 5 laboratorios del taller de microservicios y Chaos Engineering.

---

## 🏛 Arquitectura del Sistema

```text
┌─────────────────────────┐           ┌─────────────────────────┐
│     catalog-service     │           │      orders-service     │
│        (FastAPI)        │ ◄──HTTP───┤        (FastAPI)        │
│          :8001          │           │          :8002          │
└────────────┬────────────┘           └────────────┬────────────┘
             │                                     │
             └──────────────────┬──────────────────┘
                                │
                      ┌─────────┴─────────┐
                      │   Docker Network  │
                      │(coworking-network)│
                      └───────────────────┘
```

```mermaid
graph LR
    subgraph "Docker Network (coworking-network)"
        Orders[orders-service :8002] -->|GET /spaces/{id}| Catalog[catalog-service :8001]
    end
    Client([Cliente / Postman / cURL]) -->|POST /orders| Orders
    Client -->|GET /spaces| Catalog
```

---

## 📁 Estructura del Proyecto

```text
Sabado/ (o coworking-workshop/)
├── README.md                          # Guía completa paso a paso
├── docker-compose.yml                 # Orquestación de ambos servicios
├── chaos-test.sh                      # Script de simulación de caos (Bash / Linux / Mac / WSL)
├── chaos-test.ps1                     # Script de simulación de caos (PowerShell en Windows)
├── chaos-report.md                    # Reporte de análisis de fallos e impacto
├── coworking.postman_collection.json  # Colección de pruebas para Postman
├── catalog-service/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
└── orders-service/
    ├── main.py
    ├── requirements.txt
    └── Dockerfile
```

---

## 🚀 Guía de Ejecución Paso a Paso

### 🧪 LAB 1: `catalog-service` con FastAPI

**Objetivo:** Crear un microservicio que exponga espacios de coworking vía HTTP en el puerto `8001`.

#### 1. Estructura y Código
- [catalog-service/requirements.txt](file:///c:/Users/Usuario/Downloads/diplo/Sabado/catalog-service/requirements.txt)
- [catalog-service/Dockerfile](file:///c:/Users/Usuario/Downloads/diplo/Sabado/catalog-service/Dockerfile)
- [catalog-service/main.py](file:///c:/Users/Usuario/Downloads/diplo/Sabado/catalog-service/main.py)

#### 2. Prueba Local (sin Docker):
```bash
cd catalog-service
pip install -r requirements.txt
python main.py
```

En otra terminal / consola:
```bash
# Verificar salud
curl http://localhost:8001/health

# Listar todos los espacios
curl http://localhost:8001/spaces

# Consultar espacio por ID
curl http://localhost:8001/spaces/1
```

---

### 🧪 LAB 2: `orders-service` que consulta al catálogo

**Objetivo:** Crear un microservicio que gestione órdenes y consuma información de `catalog-service` vía HTTP en el puerto `8002`.

#### 1. Estructura y Código
- [orders-service/requirements.txt](file:///c:/Users/Usuario/Downloads/diplo/Sabado/orders-service/requirements.txt)
- [orders-service/Dockerfile](file:///c:/Users/Usuario/Downloads/diplo/Sabado/orders-service/Dockerfile)
- [orders-service/main.py](file:///c:/Users/Usuario/Downloads/diplo/Sabado/orders-service/main.py)

#### 2. Prueba Local:
```bash
cd orders-service
pip install -r requirements.txt
python main.py
```

*Nota:* `orders-service` utilizará por defecto `http://localhost:8001` si no está dentro de la red Docker.

---

### 🧪 LAB 3: Docker Compose con red compartida

**Objetivo:** Orquestar ambos servicios con networking interno mediante Docker Compose.

#### 1. Archivo de orquestación
- [docker-compose.yml](file:///c:/Users/Usuario/Downloads/diplo/Sabado/docker-compose.yml)

#### 2. Construir y levantar servicios:
```bash
docker-compose up --build -d
```

#### 3. Probar el flujo completo:
```bash
# 1. Ver espacios disponibles en el catálogo
curl http://localhost:8001/spaces

# 2. Crear una orden (orders-service consulta internamente a catalog-service)
curl -X POST "http://localhost:8002/orders?space_id=1&user_email=test@example.com&hours=2"

# 3. Ver órdenes creadas
curl http://localhost:8002/orders
```

---

### 🧪 LAB 4: Chaos Engineering - Apagar el catálogo

**Objetivo:** Experimentar fallos reales de sistemas distribuidos deteniendo la dependencia principal.

#### Ejecutar el Chaos Test:

- **En Bash (Linux, macOS, Git Bash o WSL):**
  ```bash
  chmod +x chaos-test.sh
  ./chaos-test.sh
  ```

- **En Windows PowerShell:**
  ```powershell
  .\chaos-test.ps1
  ```

#### Comportamiento Esperado:
1. **Primera petición:** Éxito (`200/201 OK`).
2. **Con catálogo detenido (`docker-compose stop catalog-service`):** Error `503 Service Unavailable` con detalle `"Catalog service unavailable"`.
3. **Tras reactivación (`docker-compose start catalog-service`):** Éxito (`200/201 OK`).

---

### 🧪 LAB 5: Chaos Engineering - Cambiar el contrato sin avisar

**Objetivo:** Romper la integración cambiando el contrato del API del catálogo.

#### Paso 1: Modificar `catalog-service/main.py`
Cambiar en la base de datos o modelo el campo `price_per_hour` por `hourly_rate`:
```python
# Modificación en catalog-service/main.py:
class Space(BaseModel):
    id: int
    name: str
    capacity: int
    hourly_rate: float # <-- Cambio de contrato

SPACES_DB = [
    {"id": 1, "name": "Hot Desk Flex", "capacity": 1, "hourly_rate": 15.0},
    # ...
]
```

#### Paso 2: Reconstruir y probar:
```bash
# Reconstruir el servicio con la nueva imagen
docker-compose up --build -d

# Esperar unos segundos
# Intentar crear una orden (fallará por incompatibilidad de contrato)
curl -X POST "http://localhost:8002/orders?space_id=1&user_email=contract@test.com&hours=2"
```

**Resultado esperado:**
Código `HTTP 500`:
```json
{
  "detail": "Contract violation: key 'price_per_hour' not found in catalog response"
}
```

#### Paso 3: Documentar el problema
Revisar el archivo [chaos-report.md](file:///c:/Users/Usuario/Downloads/diplo/Sabado/chaos-report.md) para el análisis de causa raíz y soluciones de resiliencia recomendadas (Versionado, Backward Compatibility y Consumer-Driven Contracts).

---

## 🛠 Comandos de Debugging Útiles

```bash
# Ver logs en tiempo real de todos los contenedores
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f catalog-service
docker-compose logs -f orders-service

# Ver estado de los contenedores
docker-compose ps

# Entrar a la terminal de un contenedor en ejecución
docker-compose exec orders-service sh

# Inspeccionar la red Docker compartida
docker network inspect sabado_coworking-network

# Probar conectividad y resolución DNS interna desde orders-service
docker-compose exec orders-service curl -s http://catalog-service:8001/health

# Reconstruir imágenes sin caché
docker-compose build --no-cache

# Detener y limpiar contenedores y redes
docker-compose down
```
