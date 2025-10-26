#!/bin/bash

COMPOSE_FILE="docker-compose-prod.yml"
BUILD=false
LOGS=false
DOWN=false
UP=false

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --dev) COMPOSE_FILE="docker-compose-dev.yml" ;;
    --build) BUILD=true ;;
    --logs) LOGS=true ;;
    --down) DOWN=true ;;
    --up) UP=true ;;
    *) echo "Неизвестный флаг: $1"; exit 1 ;;
  esac
  shift
done

if [ "$DOWN" = true ]; then
  docker compose -f $COMPOSE_FILE down
  exit 0
fi

if [ "$BUILD" = true ]; then
  docker compose -f $COMPOSE_FILE build
fi

if [ "$UP" = true ]; then
  docker compose -f $COMPOSE_FILE up -d
  docker compose -f $COMPOSE_FILE ps
fi

if [ "$LOGS" = true ]; then
  echo "Показываю логи..."
  docker compose -f $COMPOSE_FILE logs -f
else
  if [ "$UP" = true ]; then
    echo "Стек запущен успешно!"
  fi
fi
