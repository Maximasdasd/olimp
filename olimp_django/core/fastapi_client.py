"""Клиент к FastAPI-бэкенду.

Django выступает фронтендом: аутентификация и все данные берутся из FastAPI.
Схема входа:
  * пользователь логинится через /login/ -> Django шлёт логин/пароль в FastAPI
    (POST /api/auth/login, form-data);
  * FastAPI возвращает JWT, Django кладёт его в сессию (request.session['fastapi_token']);
  * все последующие запросы к FastAPI идут с заголовком Authorization: Bearer <token>.
"""
import requests
from django.conf import settings

BASE_URL = settings.FASTAPI_URL
TIMEOUT = 10


# --- Токен и заголовки ---------------------------------------------------
def get_fastapi_token(request):
    """Токен FastAPI из сессии (или None)."""
    return request.session.get("fastapi_token")


def get_headers(request):
    """Заголовок Authorization для запросов к FastAPI (или пустой словарь)."""
    token = get_fastapi_token(request)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def get_current_user(request):
    """Текущий пользователь из FastAPI (/api/auth/me) или None."""
    token = get_fastapi_token(request)
    if not token:
        return None
    cached = request.session.get("user_info")
    if cached:
        return cached
    try:
        resp = requests.get(
            f"{BASE_URL}/api/auth/me", headers=get_headers(request), timeout=TIMEOUT
        )
    except requests.RequestException:
        return None
    if resp.status_code == 200:
        user = resp.json()
        request.session["user_info"] = user
        return user
    return None


# --- Вход / выход --------------------------------------------------------
def login_to_fastapi(request, username, password):
    """Логин в FastAPI. При успехе сохраняет токен и данные пользователя в сессию.

    Возвращает (ok: bool, error: str|None).
    """
    try:
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": username, "password": password},
            timeout=TIMEOUT,
        )
    except requests.RequestException:
        return False, "Сервис бэкенда недоступен"

    if resp.status_code == 200:
        data = resp.json()
        token = data.get("access_token") or data.get("token") or data.get("accessToken")
        if not token:
            return False, "Бэкенд не вернул токен"
        request.session["fastapi_token"] = token
        request.session["user_info"] = {
            "id": data.get("user_id"),
            "username": data.get("username"),
            "role": data.get("role"),
        }
        return True, None

    detail = "Неверное имя пользователя или пароль"
    try:
        detail = resp.json().get("detail", detail)
    except ValueError:
        pass
    return False, detail


def register_student(request, payload):
    """Регистрация студента через FastAPI (POST /api/auth/register).

    При успехе сразу логинит пользователя (токен в сессию).
    Возвращает (ok, error).
    """
    try:
        resp = requests.post(
            f"{BASE_URL}/api/auth/register", json=payload, timeout=TIMEOUT
        )
    except requests.RequestException:
        return False, "Сервис бэкенда недоступен"

    if resp.status_code == 200:
        data = resp.json()
        token = data.get("access_token")
        if token:
            request.session["fastapi_token"] = token
            request.session["user_info"] = {
                "id": data.get("user_id"),
                "username": data.get("username"),
                "role": data.get("role"),
            }
        return True, None

    detail = "Не удалось зарегистрироваться"
    try:
        detail = resp.json().get("detail", detail)
    except ValueError:
        pass
    return False, detail


def logout(request):
    """Выход: чистим токен и кэш пользователя из сессии."""
    request.session.pop("fastapi_token", None)
    request.session.pop("user_info", None)


# --- Универсальные HTTP-обёртки -----------------------------------------
def api_get(request, path, params=None):
    return requests.get(
        f"{BASE_URL}{path}", headers=get_headers(request),
        params=params, timeout=TIMEOUT,
    )


def api_post(request, path, json=None, data=None):
    return requests.post(
        f"{BASE_URL}{path}", headers=get_headers(request),
        json=json, data=data, timeout=TIMEOUT,
    )


def api_put(request, path, json=None):
    return requests.put(
        f"{BASE_URL}{path}", headers=get_headers(request),
        json=json, timeout=TIMEOUT,
    )
