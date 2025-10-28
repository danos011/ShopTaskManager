# ShopTaskManager

Асинхронная обработка заказов интернет‑магазина: обработка заказов, уведомления, инвойсы PDF, периодические задачи.
Оркестрация через Docker Compose, запуск всех сервисов через `entrypoint.sh` (dev/prod), мониторинг Celery через Flower.

---

## Содержание

- Архитектура
- Требования
- Установка и запуск
- Конфигурация (.env)
- Команды entrypoint.sh (dev/prod)
- Эндпоинты API и примеры
- Очереди и задачи Celery
- Ключи в Redis
- Мониторинг (Flower)
- Разработка и отладка
- Админ‑операции (Redis, Docker)
- Траблшутинг

---

## Архитектура

Сервисы:

- `backend` — FastAPI/Uvicorn (REST API).
- `redis` — брокер сообщений / results backend / кэш.
- `workers` — Celery workers (две очереди в одном контейнере: `default`, `priority`).
- `celery_beat` — Celery Beat (ежедневные и периодические задачи).
- `flower` — мониторинг Celery с basic‑auth.

Volumes:

- `./logs` → `/app/logs` — логи приложений.
- `./docker_volumes/redis` → `/data` — данные Redis.

Сеть:

- bridge‑сеть `backend-net`.

Порты:

- API: `8000`
- Flower: `5555`
- Redis: `6379`

---

## Требования

- Docker, Docker Compose
- Открытые порты 8000/5555/6379

---

## Установка и запуск(дев среда)

1) Клонирование:

```git clone```
```cd ShopTaskManager```

2) Создать файл `.env` в корне:

```
REDIS_HOST=redis 
REDIS_PORT=6379 
CELERY_BROKER_DSN=redis://redis:6379/0 
CELERY_BACKEND_DSN=redis://redis:6379/1
FLOWER_USER=admin 
FLOWER_PASSWORD=<set_your_password>
```

3) Права на entrypoint:

```chmod +x entrypoint.sh```

4) Прод‑режим:

Полная пересборка образов

```
./entrypoint.sh –build
```

Запуск

```
./entrypoint.sh –up
```

Остановка

```
./entrypoint.sh –down
```

5) Dev‑режим (аналогичные команды с флагом `--dev`):

```
/entrypoint.sh –-dev –-build 
```

```
./entrypoint.sh –-dev -–up
```

```
./entrypoint.sh –-dev -–down
```

Проверка:

- Swagger: http://localhost:8000/docs
- Flower: http://localhost:5555 (логин `admin`, пароль из `.env`)

Примечание:

- В prod compose backend стартует через `python -m uvicorn backend.main:app ...` (или через CMD/entrypoint внутри
  Dockerfile, если так определено).
- В `workers` поднимаются два воркера в одном контейнере (очереди `default` и `priority`) согласно командам в
  compose/entrypoint.

---

## Эндпоинты API и примеры

Swagger/OpenAPI:

- http://localhost:8000/docs

Основные ручки:

- `POST /order`
    - Вход: `{"id":"123","item":"SKU-1","qty":2,"email":"user@example.com"}`
    - Действие: ставит `process_order` в очередь `default`, возвращает `task_id`.
- `GET /status/{task_id}`
    - Статус задачи Celery, результат из Redis (если готов).
- `GET /invoice/{order_id}`
    - Возвращает PDF из Redis (ключ `invoice:{order_id}`).
- `POST /test_notification`
    - Вход: `{"email":"user@example.com","message":"Hello!"}`
    - Действие: ставит `send_notification` в очередь `priority`.

Примеры:

Создать заказ

```
curl -X POST http://localhost:8000/order 
-H “Content-Type: application/json” 
-d ‘{“id”:“123”,“item”:“SKU-1”,“qty”:2,“email”:“user@example.com”}’
```

Проверить статус

```curl http://localhost:8000/status/<task_id>```

Скачать инвойс

```curl -OJ http://localhost:8000/invoice/123```

Тест уведомления (priority)

```
curl -X POST http://localhost:8000/test_notification 
-H “Content-Type: application/json” 
-d ‘{“email”:“user@example.com”,“message”:“Hello!”}’
```


---

## Очереди и задачи Celery

Очереди:
- `default` — `process_order`, `generate_invoice`, `daily_stock_report`, `check_pending_orders`
- `priority` — `send_notification`

Задачи:
- `process_order(order_id, item, qty, email)` — изменение остатков `stock:{sku}`, `order:{id}:status=processed`, инициирует инвойс.
- `send_notification(email, message)` — задержка/валидация email (`pydantic[email]`), логирование.
- `generate_invoice(order_id, data)` — PDF в памяти, запись байтов в Redis `invoice:{order_id}`.
- `daily_stock_report` — суточная агрегация `stock:*`.
- `check_pending_orders` — каждые 5 минут обрабатывает “зависшие” заказы.

Маршрутизация:
- `send_notification` → `priority`, остальное → `default`.

---

## Ключи в Redis

Шаблоны:
- `order:{order_id}:status` — строка статуса (`processed`, `failed`, ...).
- `invoice:{order_id}` — бинарный PDF (без TTL).
- `stock:{sku}` — остатки (число).
- `celery:*` — служебные ключи брокера/результатов.

Команды:
