#!/bin/bash

set -e

echo "🚀 Configurazione avvio automatico Warehouse (Docker Engine)"
echo "========================================================="

if [ "$EUID" -ne 0 ]; then
    echo "❌ Errore: Questo script deve essere eseguito come root (usa sudo)"
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_FILE="warehouse.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "📁 Directory progetto: $PROJECT_DIR"

if [ ! -f "$PROJECT_DIR/$SERVICE_FILE" ]; then
    echo "❌ Errore: File $SERVICE_FILE non trovato"
    exit 1
fi

echo "🔧 Abilitazione Docker all'avvio..."
systemctl enable docker.service
systemctl start docker.service

echo "📄 Copia del servizio systemd..."
cp "$PROJECT_DIR/$SERVICE_FILE" "$SYSTEMD_DIR/"

echo "🔄 Aggiornamento configurazione systemd..."
systemctl daemon-reload

echo "✅ Abilitazione servizio Warehouse..."
systemctl enable warehouse.service

echo ""
echo "✨ Configurazione completata!"
echo ""
echo "Comandi disponibili:"
echo "  • Avvia:     sudo systemctl start warehouse"
echo "  • Ferma:     sudo systemctl stop warehouse"
echo "  • Restart:   sudo systemctl restart warehouse"
echo "  • Status:    sudo systemctl status warehouse"
echo "  • Log:       sudo journalctl -u warehouse -f"
echo ""
echo "🎉 All'avvio del PC, Warehouse si avvierà automaticamente!"
