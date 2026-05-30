# Олимпиадное движение — REST API (FastAPI)

АРМ для обработки информации об участии студентов в олимпиадном движении и
конкурсах профессионального мастерства.

## Архитектура (MVC)

Проект построен по схеме **MVC (Model–View–Controller)**:

| Слой | Каталог | Назначение |
|------|---------|------------|
| **Model** | `app/models/` (ORM) + `app/schemas/` (Pydantic) | Данные и их структура |
| **Controller** | `app/controllers/` | Бизнес-логика и работа с БД |
| **View** | `app/routers/` | HTTP-эндпоинты (тонкие, вызывают контроллеры) |
| Вспомогательное | `app/dependencies/`, `app/utils/`, `app/db/` | Аутентификация, конфиг, подключение к БД |

Роутеры (**View**) не обращаются к БД напрямую — вся логика вынесена в
контроллеры (**Controller**), а структура данных описана в моделях и схемах
(**Model**).

## Аутентификация

Вход выполняется **по логину и паролю** (схема OAuth2 `password`).
Токены **не нужно вставлять вручную**: в Swagger UI (`/docs`) нажмите кнопку
**Authorize**, введите username и пароль — токен будет подставляться
автоматически во все запросы.

- `POST /api/auth/register` — регистрация
- `POST /api/auth/login` — вход (форма username + password) → access-токен
- `GET /api/auth/me` — текущий пользователь

Роли: `admin`, `teacher`, `student`.

## Запуск

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

По умолчанию используется SQLite (файл `olimp.db`) — настройка БД не требуется.
Для PostgreSQL задайте переменные окружения (можно через файл `.env`):

```
DATABASE_URL=postgresql://user:password@localhost/olimpiad
SECRET_KEY=your-secret-key
```

Документация API: http://127.0.0.1:8000/docs

## Тесты

```bash
pytest
```
