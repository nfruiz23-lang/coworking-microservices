
# Informe de Chaos Engineering: Coworking Workshop

Este documento recopila el análisis post-mortem y los hallazgos de las pruebas de Chaos Engineering realizadas sobre la arquitectura de microservicios (`catalog-service` y `orders-service`).

---

## Test 1: Caída de servicio dependiente

- **Escenario**:
  Simulación de fallo total del microservicio `catalog-service` mientras `orders-service` sigue recibiendo peticiones entrantes de reserva de espacios de trabajo (`POST /orders`).
  
- **Impacto**:
  - Los usuarios no pueden crear nuevas órdenes que requieran consultar el catálogo.
  - La llamada HTTP cliente `httpx.get` en `orders-service` experimenta un fallo de conexión (`httpx.RequestError`).
  - Gracias al bloque de resiliencia implementado en `orders-service`, el error es capturado y mapeado a un código de estado `HTTP 503 (Service Unavailable)` con el mensaje `"Catalog service unavailable"`, en lugar de propagar un fallo de aplicación no controlado (`HTTP 500`).
  
- **Tiempo de detección**:
  - Inmediato al término del timeout configurado (3.0 segundos en el cliente HTTP) o rechazo de conexión TCP instantáneo (`ECONNREFUSED`).
  
- **Recuperación**:
  - Una vez reactivado el contenedor `catalog-service` (`docker-compose start catalog-service`), el servicio vuelve a responder exitosamente (`HTTP 200/201`) sin necesidad de reiniciar `orders-service`.
  - **Mejora recomendada**: Implementar un patrón **Circuit Breaker** (como PyBreaker o Resilience4j en gateways) y mecanismos de caché local (Redis o en memoria) para datos estáticos del catálogo, permitiendo operar en modo degradado temporalmente.

---

## Test 2: Cambio de contrato sin versionar (Breaking Change)

- **Escenario**:
  El equipo de `catalog-service` modifica el nombre del campo `price_per_hour` por `hourly_rate` en la respuesta JSON del endpoint `/spaces/{space_id}`, sin actualizar la versión de la API ni coordinar el cambio con el servicio consumidor `orders-service`.

- **Impacto**:
  - `orders-service` recibe un JSON válido (`HTTP 200`) del catálogo, pero al intentar procesar `space["price_per_hour"]`, el campo no existe.
  - Se genera una excepción de violación de contrato (`KeyError` / `HTTP 500`), interrumpiendo el flujo de ventas para todos los clientes que intentan reservar.
  - Falso positivo a nivel de red: la red funciona, el catálogo responde con 200 OK, pero la integración semántica está rota.

- **Causa raíz**:
  - Falta de gobernanza en la evolución de APIs y ausencia de versionado semántico en la URL (por ejemplo `/v1/spaces` vs `/v2/spaces`).
  - Desacoplamiento de contratos sin pruebas de integración dirigidas por el consumidor (Consumer-Driven Contract Testing).

- **Solución propuesta**:
  1. **Versionado de APIs**: Mantener `/api/v1/spaces` compatible y publicar nuevas versiones en `/api/v2/spaces`.
  2. **Compatibilidad hacia atrás (Backward Compatibility)**: Durante periodos de migración, exponer ambos campos simultáneamente:
     ```python
     return {
         "id": space["id"],
         "name": space["name"],
         "price_per_hour": space["price_per_hour"],  # Deprecated
         "hourly_rate": space["price_per_hour"]      # Nuevo estándar
     }
     ```
  3. **Contract Testing**: Implementar pruebas de contrato automatizadas en el pipeline de CI/CD utilizando herramientas como **Pact** o esquemas OpenAPI/JSON Schema validados en tiempo de compilación/test.
