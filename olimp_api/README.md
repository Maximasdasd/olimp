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

## База данных — PostgreSQL

Основное хранилище проекта — **PostgreSQL** (общая БД для всей системы;
Django-фронтенд `../olimp_django` ходит за данными в этот бэкенд).

Создание БД:

```bash
sudo -u postgres psql -c "CREATE DATABASE olimpiad;"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'root';"
```

Скопируйте `.env.example` в `.env` и при необходимости поправьте параметры:

```
DATABASE_URL=postgresql://postgres:root@localhost:5432/olimpiad
SECRET_KEY=super-secret-key-change-me
```

> Если `DATABASE_URL` не задан, используется SQLite (`olimp.db`) —
> удобно для быстрых запусков и тестов.

## Запуск

```bash
pip install -r requirements.txt
# переменные окружения берутся из .env
uvicorn app.main:app --reload
```

Документация API: http://127.0.0.1:8000/docs

### Демонстрационные данные

```bash
python -m scripts.seed_data
```

Создаёт учётки `admin/admin123`, `teacher/teacher123`, `student/student123`,
пару олимпиад и опубликованный протокол.

## Тесты

```bash
pytest
```

Тесты используют отдельную SQLite-БД в памяти и не затрагивают PostgreSQL.
