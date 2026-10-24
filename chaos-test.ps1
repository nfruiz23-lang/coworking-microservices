Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   CHAOS ENGINEERING TEST: Simulacion Caida Catalogo" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "[Paso 1] Probando estado normal (Catalogo encendido)..." -ForegroundColor Yellow
try {
    $url1 = 'http://localhost:8002/orders?space_id=1&user_email=normal@example.com&hours=2'
    $resp1 = Invoke-RestMethod -Uri $url1 -Method Post
    Write-Host "Peticion exitosa con catalogo operativo." -ForegroundColor Green
    $resp1 | ConvertTo-Json
} catch {
    Write-Host "Error en la peticion inicial: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[Paso 2] Deteniendo 'catalog-service' intencionalmente..." -ForegroundColor Yellow
docker-compose stop catalog-service
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "[Paso 3] Probando orden con el catalogo caido..." -ForegroundColor Yellow
$url2 = 'http://localhost:8002/orders?space_id=1&user_email=chaos@example.com&hours=2'
try {
    $resp2 = Invoke-WebRequest -Uri $url2 -Method Post -ErrorAction Stop
    Write-Host "Respuesta inesperada: $($resp2.StatusCode)" -ForegroundColor Red
} catch {
    $status = 0
    if ($_.Exception.Response) {
        $status = [int]$_.Exception.Response.StatusCode
    }
    Write-Host "Codigo HTTP capturado: $status" -ForegroundColor Yellow
    if ($status -eq 503) {
        Write-Host "Comportamiento esperado: Error 503 'Catalog service unavailable' capturado." -ForegroundColor Green
    } else {
        Write-Host "Se obtuvo: $status ($($_.Exception.Message))" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[Paso 4] Recuperando 'catalog-service'..." -ForegroundColor Yellow
docker-compose start catalog-service
Write-Host "Esperando 6 segundos a que el contenedor este listo..."
Start-Sleep -Seconds 6

Write-Host ""
Write-Host "[Paso 5] Probando recuperacion del sistema..." -ForegroundColor Yellow
$url3 = 'http://localhost:8002/orders?space_id=1&user_email=recovered@example.com&hours=2'
try {
    $resp3 = Invoke-RestMethod -Uri $url3 -Method Post
    Write-Host "Respuesta exitosa tras reinicio:" -ForegroundColor Green
    $resp3 | ConvertTo-Json
    Write-Host "Sistema completamente recuperado (Resiliencia verificada)." -ForegroundColor Green
} catch {
    Write-Host "Error tras recuperacion: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "                 Test finalizado                    " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
