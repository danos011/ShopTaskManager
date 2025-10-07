#!/bin/bash

COMPOSE_FILE="docker-compose-prod.yml"

BUILD=false
LOGS=false
DOWN=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --build) BUILD=true ;;
        --logs) LOGS=true ;;
        --down) DOWN=true ;;
        *) echo "Неизвестный флаг: $1"; exit 1 ;;
    esac
    shift
done

# Если указан --down, останавливаем и выходим
if [ "$DOWN" = true ]; then
    docker compose -f $COMPOSE_FILE down
    exit 0
fi

# Если указан --build, пересобираем образы
if [ "$BUILD" = true ]; then
    docker compose -f $COMPOSE_FILE build
fi

# Запускаем контейнеры
docker compose -f $COMPOSE_FILE up -d

# Показываем статус
docker compose -f $COMPOSE_FILE ps

# Если указан --logs, показываем логи
if [ "$LOGS" = true ]; then
    echo "Показываю логи..."
    docker compose -f $COMPOSE_FILE logs -f
else
    echo "Стек запущен успешно!"
fi
