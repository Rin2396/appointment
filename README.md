# Appointment Hub (Backend)

Монолит на FastAPI с PostgreSQL, Redis (кеш), RabbitMQ (события) и воркером уведомлений (Telegram).

## Требования
- Docker / Docker Compose
- Python 3.11+ (для локального запуска/тестов)
- Poetry

## Быстрый старт (через Docker)
1. Скопировать `.env.example` → `.env` и заполнить (DB, Redis, RabbitMQ, Telegram).
2. Собрать и поднять:
   ```bash
   docker compose build
   docker compose up -d
   ```
3. Применить миграции:
   ```bash
   docker compose exec api alembic upgrade head
   ```
4. API: `http://localhost:8000/api/v1`, Swagger: `http://localhost:8000/docs`.
5. Проверка health: `curl http://localhost:8000/health`.

## Локальные тесты
```bash
poetry install
poetry run pytest --cov=app
```

## Telegram уведомления (как настроить и проверить)
1. Создать бота через BotFather, получить `TELEGRAM__BOT_TOKEN`.
2. Добавить бота в нужный чат/группу/канал и дать право писать (для канала — сделать админом).
3. Узнать `chat_id`:
   - Написать сообщение в чат/группу/канал.
   - Выполнить:  
     ```bash
     curl "https://api.telegram.org/bot$TELEGRAM__BOT_TOKEN/getUpdates"
     ```
   - В ответе взять `chat.id` (для групп/каналов обычно отрицательный `-100...`).
4. Записать в `.env`:
   ```
   TELEGRAM__BOT_TOKEN=...
   TELEGRAM__CHAT_ID=<NEGATIVE_CHAT_ID>
   ```
5. Перезапустить сервисы (`docker compose up -d`), затем создать/отменить запись — воркер отправит сообщение.
   Для ручной проверки:
   ```bash
   curl -X POST "https://api.telegram.org/bot$TELEGRAM__BOT_TOKEN/sendMessage" \
     -H "Content-Type: application/json" \
     -d '{"chat_id":"<NEGATIVE_CHAT_ID>","text":"ping"}'
   ```

## Основные команды (Taskfile)
- `task up` — `docker-compose up -d --build`
- `task down` — остановить
- `task db:migrate` — миграции через api-контейнер
- `task test` — pytest с coverage
- `task logs` — tail логов

## Стек и модули
- API: FastAPI (/api/v1)
- Домены: users, services, schedules (slots), appointments, notifications
- Хранилища: PostgreSQL (async SQLAlchemy, Alembic)
- Кеш: Redis (списки услуг и слотов с TTL, инвалидация при изменениях)
- События: RabbitMQ (appointment.created/cancelled), воркер-уведомитель (Telegram)

