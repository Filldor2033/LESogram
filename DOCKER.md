# Docker запуск LESogram

## 1. Сборка и запуск

```bash
docker compose up --build
```

После запуска приложение будет доступно по адресу:

`http://localhost:8000`

## 2. Запуск в фоне

```bash
docker compose up -d --build
```

## 3. Остановка

```bash
docker compose down
```

## 4. Где хранятся данные

- SQLite БД хранится в volume `lesogram_data` (`/app/data/chat.db` внутри контейнера).
- Загруженные файлы хранятся в volume `lesogram_uploads` (`/app/src/uploads` внутри контейнера).

## 5. Важные переменные

- `SECRET_KEY` - ключ подписи JWT. В `docker-compose.yml` замените `change-me-in-production` на свой.
- `DATABASE_URL` - строка подключения к БД.
