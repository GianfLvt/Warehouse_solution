#!/bin/bash

set -e

echo "🚀 Configurazione avvio automatico Warehouse"
echo "=========================================="

if docker info >/dev/null 2>&1; then
    echo "✅ Docker Desktop rilevato"
else
    echo "❌ Errore: Docker Desktop non è in esecuzione"
    echo "   Avvia Docker Desktop e riprova"
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUTOSTART_DIR="$HOME/.config/autostart"

echo "📁 Directory progetto: $PROJECT_DIR"

mkdir -p "$AUTOSTART_DIR"

echo "📄 Configurazione avvio automatico Docker Desktop..."
if [ ! -f "$AUTOSTART_DIR/docker-desktop.desktop" ]; then
    cp "$AUTOSTART_DIR/docker-desktop.desktop" "$AUTOSTART_DIR/docker-desktop.desktop.backup" 2>/dev/null || true
fi

cat > "$AUTOSTART_DIR/docker-desktop.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Docker Desktop
Exec=/opt/docker-desktop/bin/docker-desktop
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Icon=/opt/docker-desktop/share/icon.original.png
Comment=Start Docker Desktop at login
EOF

echo "📄 Configurazione avvio automatico Warehouse..."
cat > "$AUTOSTART_DIR/warehouse-webapp.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Warehouse Webapp
Exec=$PROJECT_DIR/start-warehouse-after-docker.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Start Warehouse webapp after Docker Desktop
X-GNOME-Autostart-Delay=10
EOF

chmod +x "$PROJECT_DIR/start-warehouse-after-docker.sh"

echo ""
echo "✨ Configurazione completata!"
echo ""
echo "Comandi disponibili:"
echo "  • Avvia:     ./manage.sh start"
echo "  • Ferma:     ./manage.sh stop"
echo "  • Restart:   ./manage.sh restart"
echo "  • Status:    ./manage.sh status"
echo "  • Log:       docker compose -f docker-compose.yml logs -f"
echo ""
echo "📂 File autostart creati in: $AUTOSTART_DIR"
echo "🎉 Al prossimo riavvio, Docker Desktop e Warehouse si avvieranno automaticamente!"
