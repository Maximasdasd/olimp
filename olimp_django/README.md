# Олимпиадное движение — фронтенд (Django)

Веб-интерфейс (фронтенд) системы учёта участия студентов в олимпиадном движении.
Django **не хранит предметные данные** и **не использует собственную модель
пользователя** — это слой представления, который общается с FastAPI-бэкендом
(`../olimp_api`) по HTTP. Единая база данных — **PostgreSQL** — принадлежит FastAPI.

## Архитектура

```
PostgreSQL  ←—  FastAPI (бэкенд, olimp_api)  ←——HTTP/JWT——  Django (фронтенд, olimp_django)
                                                              ↑
                                                          браузер
```

- Пользователь логинится через `/login/` → Django отправляет логин/пароль в
  FastAPI (`POST /api/auth/login`, form-data).
- FastAPI возвращает JWT, Django сохраняет его в сессии (`request.session['fastapi_token']`).
- Все страницы берут данные из FastAPI через `requests` с заголовком
  `Authorization: Bearer <token>`.

Собственная SQLite-база Django используется **только для сессий**, не для данных.

## Структура

```
olimp_django/
├── config/              # настройки Django, urls, wsgi/asgi
├── core/
│   ├── fastapi_client.py    # клиент к FastAPI (токен в сессии, requests)
│   ├── views.py             # вьюхи-прокси к FastAPI
│   ├── decorators.py        # контроль доступа по ролям (из сессии)
│   ├── context_processors.py# текущий пользователь во всех шаблонах
│   ├── urls.py
│   └── templates/core/      # HTML-шаблоны
├── tests/               # pytest (FastAPI замокан)
├── manage.py
└── requirements.txt
```

## Запуск

> Сначала должен быть запущен бэкенд FastAPI на `http://127.0.0.1:8000`
> (см. `../olimp_api/README.md`).

```bash
pip install -r requirements.txt
python manage.py migrate          # таблицы сессий Django (SQLite)
python manage.py runserver 8080   # фронтенд на 8080, чтобы не занять порт FastAPI
```

Откройте http://127.0.0.1:8080/

Адрес бэкенда настраивается переменной окружения `FASTAPI_URL`
(по умолчанию `http://127.0.0.1:8000`).

### Тестовые учётные записи

Создаются сидером бэкенда (`python -m scripts.seed_data` в `olimp_api`):

| Роль | Логин | Пароль |
|------|-------|--------|
| Администратор | `admin` | `admin123` |
| Преподаватель | `teacher` | `teacher123` |
| Студент | `student` | `student123` |

## Тестирование

Тесты на `pytest` + `pytest-django` в папке `tests/`. FastAPI замокан, поэтому
запущенный бэкенд для них не нужен.

| Файл | Назначение |
|------|------------|
| `conftest.py` | Фикстуры: клиенты по ролям (токен в сессии), мок FastAPI |
| `test_fastapi_client.py` | Клиент к FastAPI: токен, заголовки, логин/регистрация/выход |
| `test_views.py` | Вьюхи: публичные страницы, редиректы, права по ролям, вход/регистрация |
| `test_integration.py` | Сквозные сценарии (запись на олимпиаду, жизненный цикл протокола, отчёты) |
| `test_selenium.py` | E2E через Selenium (опционально, по умолчанию пропускаются) |

```bash
pytest                 # обычный прогон (Selenium-тесты пропускаются)
pytest -m selenium     # только E2E (нужны selenium, Chrome и запущенные сервисы)
```
