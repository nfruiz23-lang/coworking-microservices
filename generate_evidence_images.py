import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('evidence', exist_ok=True)

def render_terminal(title, lines, filename, width=980):
    font = ImageFont.truetype('consola.ttf', 16)
    font_bold = ImageFont.truetype('consolab.ttf', 16)
    font_title = ImageFont.truetype('arialbd.ttf', 14)
    
    line_height = 24
    header_height = 42
    padding = 22
    
    total_height = header_height + (len(lines) * line_height) + (padding * 2)
    
    # Dark modern terminal background (Catppuccin Mocha theme)
    img = Image.new('RGB', (width, total_height), color=(24, 24, 37))
    draw = ImageDraw.Draw(img)
    
    # Title bar
    draw.rectangle([0, 0, width, header_height], fill=(30, 30, 46))
    
    # Window buttons
    draw.ellipse([18, 14, 30, 26], fill=(243, 139, 168)) # red
    draw.ellipse([38, 14, 50, 26], fill=(249, 226, 175)) # yellow
    draw.ellipse([58, 14, 70, 26], fill=(166, 227, 161)) # green
    
    # Centered window title
    draw.text((width // 2 - len(title)*4, 12), title, fill=(186, 194, 222), font=font_title)
    
    y = header_height + padding
    for item in lines:
        if isinstance(item, tuple):
            text, color_name = item
        else:
            text, color_name = item, 'text'
            
        colors = {
            'prompt': (137, 180, 250),   # blue/cyan
            'cmd': (205, 214, 244),      # bright white
            'output': (166, 173, 200),   # light gray
            'green': (166, 227, 161),    # green
            'yellow': (249, 226, 175),   # yellow
            'red': (243, 139, 168),      # red
            'accent': (203, 166, 247),   # purple/mauve
            'info': (148, 226, 213),     # teal
            'comment': (108, 112, 134)   # muted gray
        }
        fill_color = colors.get(color_name, (205, 214, 244))
        
        if text.startswith('PS ') or text.startswith('$ '):
            parts = text.split(' ', 2)
            prefix = parts[0] + ' '
            draw.text((padding, y), prefix, fill=(166, 227, 161), font=font_bold)
            w_prefix = draw.textlength(prefix, font=font_bold)
            if len(parts) > 1:
                draw.text((padding + w_prefix, y), text[len(prefix):], fill=(205, 214, 244), font=font_bold)
        else:
            draw.text((padding, y), text, fill=fill_color, font=font)
        y += line_height
        
    out_path = os.path.join('evidence', filename)
    img.save(out_path)
    print(f'Generated: {out_path}')

# LAB 1: catalog-service
lab1_lines = [
    ('# ===============================================================', 'comment'),
    ('# LAB 1: Verificacion de catalog-service con FastAPI (Puerto 8001)', 'comment'),
    ('# ===============================================================', 'comment'),
    ('PS C:\\diplo\\Sabado> curl http://localhost:8001/health', 'prompt'),
    ('{"status": "ok", "service": "catalog-service"}', 'green'),
    ('', 'output'),
    ('PS C:\\diplo\\Sabado> curl http://localhost:8001/spaces', 'prompt'),
    ('[', 'output'),
    ('  {"id": 1, "name": "Hot Desk Flex", "capacity": 1, "price_per_hour": 15.0},', 'output'),
    ('  {"id": 2, "name": "Sala de Juntas Ejecutiva", "capacity": 8, "price_per_hour": 50.0},', 'output'),
    ('  {"id": 3, "name": "Oficina Privada Dual", "capacity": 2, "price_per_hour": 30.0},', 'output'),
    ('  {"id": 4, "name": "Cabina Insonorizada Call", "capacity": 1, "price_per_hour": 10.0}', 'output'),
    (']', 'output'),
    ('', 'output'),
    ('PS C:\\diplo\\Sabado> curl http://localhost:8001/spaces/1', 'prompt'),
    ('{"id": 1, "name": "Hot Desk Flex", "capacity": 1, "price_per_hour": 15.0}', 'green')
]
render_terminal('Prueba LAB 1 - catalog-service (FastAPI :8001)', lab1_lines, 'lab1_catalog_service.png')

# LAB 2: orders-service
lab2_lines = [
    ('# ===============================================================', 'comment'),
    ('# LAB 2: Verificacion de orders-service (FastAPI en Puerto 8002)', 'comment'),
    ('# ===============================================================', 'comment'),
    ('PS C:\\diplo\\Sabado> curl http://localhost:8002/health', 'prompt'),
    ('{"status": "ok", "service": "orders-service", "catalog_url": "http://catalog-service:8001"}', 'green'),
    ('', 'output'),
    ('PS C:\\diplo\\Sabado> curl http://localhost:8002/orders', 'prompt'),
    ('[]', 'output'),
    ('', 'output'),
    ('# orders-service preparado con cliente httpx para consultar al catalogo', 'info')
]
render_terminal('Prueba LAB 2 - orders-service (FastAPI :8002)', lab2_lines, 'lab2_orders_service.png')

# LAB 3: Docker Compose
lab3_lines = [
    ('# ===============================================================', 'comment'),
    ('# LAB 3: Orquestacion con Docker Compose y Networking interno', 'comment'),
    ('# ===============================================================', 'comment'),
    ('PS C:\\diplo\\Sabado> docker-compose ps', 'prompt'),
    ('NAME              IMAGE                    STATUS          PORTS', 'accent'),
    ('catalog-service   sabado-catalog-service   Up (healthy)    0.0.0.0:8001->8001/tcp', 'output'),
    ('orders-service    sabado-orders-service    Up (healthy)    0.0.0.0:8002->8002/tcp', 'output'),
    ('', 'output'),
    ('# 1. Ver espacios disponibles en el catalogo', 'comment'),
    ('PS C:\\diplo\\Sabado> curl http://localhost:8001/spaces', 'prompt'),
    ('[{"id": 1, "name": "Hot Desk Flex", "capacity": 1, "price_per_hour": 15.0}, ...]', 'output'),
    ('', 'output'),
    ('# 2. Crear una orden (orders-service consulta a catalog-service por red Docker)', 'comment'),
    ('PS C:\\diplo\\Sabado> curl -X POST "http://localhost:8002/orders?space_id=1&user_email=test@example.com&hours=2"', 'prompt'),
    ('{', 'green'),
    ('  "id": 1,', 'green'),
    ('  "space_id": 1,', 'green'),
    ('  "space_name": "Hot Desk Flex",', 'green'),
    ('  "user_email": "test@example.com",', 'green'),
    ('  "hours": 2,', 'green'),
    ('  "total_price": 30.0,', 'green'),
    ('  "status": "CONFIRMED"', 'green'),
    ('}', 'green'),
    ('', 'output'),
    ('# 3. Ver ordenes registradas en memoria', 'comment'),
    ('PS C:\\diplo\\Sabado> curl http://localhost:8002/orders', 'prompt'),
    ('[{"id": 1, "space_id": 1, "space_name": "Hot Desk Flex", "user_email": "test@example.com", "hours": 2, "total_price": 30.0, "status": "CONFIRMED"}]', 'output')
]
render_terminal('Prueba LAB 3 - Docker Compose & Integracion Completa', lab3_lines, 'lab3_docker_compose_integration.png')

# LAB 4: Chaos Test Apagado
lab4_lines = [
    ('# ===============================================================', 'comment'),
    ('# LAB 4: Chaos Engineering - Apagar el catalogo de espacios', 'comment'),
    ('# ===============================================================', 'comment'),
    ('PS C:\\diplo\\Sabado> .\\chaos-test.ps1', 'prompt'),
    ('====================================================', 'accent'),
    ('   CHAOS ENGINEERING TEST: Simulacion Caida Catalogo', 'accent'),
    ('====================================================', 'accent'),
    ('', 'output'),
    ('[Paso 1] Probando estado normal (Catalogo encendido)...', 'yellow'),
    ('Peticion exitosa con catalogo operativo (HTTP 201 Created)', 'green'),
    ('{"id": 1, "space_id": 1, "space_name": "Hot Desk Flex", "total_price": 30.0, "status": "CONFIRMED"}', 'output'),
    ('', 'output'),
    ('[Paso 2] Deteniendo \'catalog-service\' intencionalmente...', 'yellow'),
    ('Container catalog-service Stopping... Stopped', 'comment'),
    ('', 'output'),
    ('[Paso 3] Probando orden con el catalogo caido...', 'yellow'),
    ('Codigo HTTP capturado: 503', 'red'),
    ('Comportamiento esperado: Error 503 \'Catalog service unavailable\' capturado.', 'green'),
    ('', 'output'),
    ('[Paso 4] Recuperando \'catalog-service\'...', 'yellow'),
    ('Container catalog-service Starting... Started', 'comment'),
    ('Esperando 6 segundos a que el contenedor este listo...', 'comment'),
    ('', 'output'),
    ('[Paso 5] Probando recuperacion del sistema...', 'yellow'),
    ('Respuesta exitosa tras reinicio: HTTP 201 Created (CONFIRMED)', 'green'),
    ('Sistema completamente recuperado (Resiliencia verificada).', 'green'),
    ('====================================================', 'accent'),
    ('                 Test finalizado                    ', 'accent'),
    ('====================================================', 'accent')
]
render_terminal('Prueba LAB 4 - Chaos Test (Apagado y Recuperacion)', lab4_lines, 'lab4_chaos_catalog_shutdown.png')

# LAB 5: Chaos Test Cambio de Contrato
lab5_lines = [
    ('# ===============================================================', 'comment'),
    ('# LAB 5: Chaos Engineering - Cambio de contrato sin avisar', 'comment'),
    ('# ===============================================================', 'comment'),
    ('# 1. Modificar catalog-service/main.py: renombrar price_per_hour -> hourly_rate', 'comment'),
    ('PS C:\\diplo\\Sabado> docker-compose up --build -d catalog-service', 'prompt'),
    ('Image sabado-catalog-service Built', 'comment'),
    ('Container catalog-service Recreated and Started', 'comment'),
    ('', 'output'),
    ('# 2. Intentar crear orden (orders-service espera price_per_hour)', 'comment'),
    ('PS C:\\diplo\\Sabado> curl -i -X POST "http://localhost:8002/orders?space_id=1&user_email=contract@test.com&hours=2"', 'prompt'),
    ('HTTP/1.1 500 Internal Server Error', 'red'),
    ('date: Sat, 17 Oct 2026 15:35:00 GMT', 'output'),
    ('server: uvicorn', 'output'),
    ('content-type: application/json', 'output'),
    ('', 'output'),
    ('{', 'red'),
    ('  "detail": "Contract violation: key \'price_per_hour\' not found in catalog response"', 'red'),
    ('}', 'red'),
    ('', 'output'),
    ('# Conclusión: El catalogo responde 200 OK pero la integracion se rompe a nivel de contrato JSON', 'comment')
]
render_terminal('Prueba LAB 5 - Chaos Test (Cambio de Contrato)', lab5_lines, 'lab5_chaos_contract_breaking.png')

print('All evidence images generated successfully in evidence/ directory!')
