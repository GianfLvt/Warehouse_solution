#!/bin/bash

COMMAND=$1
COMPOSE_FILE="docker-compose.yml"

case "$COMMAND" in
    start)
        echo "🚀 Avvio Warehouse..."
        docker compose -f $COMPOSE_FILE up -d
        echo "✅ Warehouse avviato!"
        ;;
    stop)
        echo "🛑 Arresto Warehouse..."
        docker compose -f $COMPOSE_FILE down
        echo "✅ Warehouse arrestato!"
        ;;
    restart)
        echo "🔄 Riavvio Warehouse..."
        docker compose -f $COMPOSE_FILE restart
        echo "✅ Warehouse riavviato!"
        ;;
    status)
        echo "📊 Status Warehouse:"
        docker compose -f $COMPOSE_FILE ps
        ;;
    logs)
        echo "📋 Log Warehouse (Ctrl+C per uscire):"
        docker compose -f $COMPOSE_FILE logs -f
        ;;
    build)
        echo "🔨 Build Warehouse..."
        docker compose -f $COMPOSE_FILE build
        echo "✅ Build completata!"
        ;;
    rebuild)
        echo "🔨 Rebuild e riavvio Warehouse..."
        docker compose -f $COMPOSE_FILE up -d --build
        echo "✅ Rebuild completata!"
        ;;
    enable)
        echo "✅ Abilitazione avvio automatico..."
        ./setup-autostart.sh
        ;;
    disable)
        echo "❌ Disabilitazione avvio automatico..."
        ./remove-autostart.sh
        ;;
    *)
        echo "🎉 Warehouse - Gestione Servizio"
        echo "=============================="
        echo ""
        echo "Uso: ./manage.sh [comando]"
        echo ""
        echo "Comandi disponibili:"
        echo "  start      - Avvia l'applicazione"
        echo "  stop       - Ferma l'applicazione"
        echo "  restart    - Riavvia l'applicazione"
        echo "  status     - Mostra lo stato del servizio"
        echo "  logs       - Mostra i log in tempo reale"
        echo "  build      - Ricostruisce le immagini"
        echo "  rebuild    - Ricostruisce e riavvia"
        echo "  enable     - Abilita avvio automatico"
        echo "  disable    - Disabilita avvio automatico"
        echo ""
        exit 1
        ;;
esac
