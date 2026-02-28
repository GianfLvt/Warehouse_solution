#!/bin/bash

set -e

echo "🗑️  Rimozione avvio automatico Warehouse"
echo "======================================"

AUTOSTART_DIR="$HOME/.config/autostart"

echo "🛑 Arresto Warehouse..."
cd "$(dirname "$0")"
docker compose -f docker-compose.yml down 2>/dev/null || true

echo "🗑️  Rimozione file autostart..."
rm -f "$AUTOSTART_DIR/warehouse-webapp.desktop"

echo "📋 Vuoi rimuovere anche l'avvio automatico di Docker Desktop? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    rm -f "$AUTOSTART_DIR/docker-desktop.desktop"
    echo "✅ Avvio automatico di Docker Desktop rimosso"
else
    echo "ℹ️  Docker Desktop continuerà ad avviarsi automaticamente"
fi

echo ""
echo "✅ Avvio automatico di Warehouse rimosso con successo!"
echo ""
echo "Per gestire manualmente:"
echo "  ./manage.sh start    - Avvia Warehouse"
echo "  ./manage.sh stop     - Ferma Warehouse"
