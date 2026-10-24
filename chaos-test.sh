#!/usr/bin/env bash

# Colores para la salida
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}   CHAOS ENGINEERING TEST: Simulación Caída Catálogo ${NC}"
echo -e "${BLUE}====================================================${NC}"

echo -e "\n${YELLOW}[Paso 1] Probando estado normal (Catálogo encendido)...${NC}"
HTTP_STATUS=$(curl -s -o /tmp/chaos_resp1.json -w "%{http_code}" -X POST "http://localhost:8002/orders?space_id=1&user_email=normal@example.com&hours=2")
echo -e "Código HTTP: ${HTTP_STATUS}"
cat /tmp/chaos_resp1.json
echo ""
if [ "$HTTP_STATUS" -eq 200 ] || [ "$HTTP_STATUS" -eq 201 ]; then
    echo -e "${GREEN}✓ Petición exitosa con catálogo operativo.${NC}"
else
    echo -e "${RED}✗ Falló la petición inicial. Asegúrate de tener docker-compose up corriendo.${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[Paso 2] Deteniendo 'catalog-service' intencionalmente...${NC}"
docker-compose stop catalog-service
sleep 2

echo -e "\n${YELLOW}[Paso 3] Probando orden con el catálogo caído...${NC}"
HTTP_STATUS_DOWN=$(curl -s -o /tmp/chaos_resp2.json -w "%{http_code}" -X POST "http://localhost:8002/orders?space_id=1&user_email=chaos@example.com&hours=2")
echo -e "Código HTTP: ${HTTP_STATUS_DOWN}"
cat /tmp/chaos_resp2.json
echo ""
if [ "$HTTP_STATUS_DOWN" -eq 503 ]; then
    echo -e "${GREEN}✓ Comportamiento esperado: Error 503 'Catalog service unavailable' manejado correctamente.${NC}"
else
    echo -e "${RED}✗ Se esperaba 503, se obtuvo: ${HTTP_STATUS_DOWN}${NC}"
fi

echo -e "\n${YELLOW}[Paso 4] Recuperando 'catalog-service'...${NC}"
docker-compose start catalog-service
echo "Esperando 6 segundos a que el servicio inicialice..."
sleep 6

echo -e "\n${YELLOW}[Paso 5] Probando recuperación del sistema...${NC}"
HTTP_STATUS_RECOVERED=$(curl -s -o /tmp/chaos_resp3.json -w "%{http_code}" -X POST "http://localhost:8002/orders?space_id=1&user_email=recovered@example.com&hours=2")
echo -e "Código HTTP: ${HTTP_STATUS_RECOVERED}"
cat /tmp/chaos_resp3.json
echo ""
if [ "$HTTP_STATUS_RECOVERED" -eq 200 ] || [ "$HTTP_STATUS_RECOVERED" -eq 201 ]; then
    echo -e "${GREEN}✓ Sistema completamente recuperado (Resiliencia verificada).${NC}"
else
    echo -e "${RED}✗ El servicio no respondió con éxito tras la recuperación.${NC}"
fi

echo -e "\n${BLUE}====================================================${NC}"
echo -e "${BLUE}                 Test finalizado                    ${NC}"
echo -e "${BLUE}====================================================${NC}"
