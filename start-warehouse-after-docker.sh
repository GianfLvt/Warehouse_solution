#!/bin/bash

set -e

echo "⏳ Attendo avvio di Docker Desktop..."

timeout=60
elapsed=0

while [ $elapsed -lt $timeout ]; do
    if docker info >/dev/null 2>&1; then
        echo "✅ Docker Desktop è pronto!"
        
        cd /home/gralogic/Scrivania/Warehouse_solution
        
        echo "🚀 Avvio Warehouse..."
        docker compose -f docker-compose.yml up -d
        
        echo "✨ Warehouse avviato con successo!"
        exit 0
    fi
    
    sleep 2
    elapsed=$((elapsed + 2))
done

echo "❌ Timeout: Docker Desktop non si è avviato in $timeout secondi"
exit 1
