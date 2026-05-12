# Recipe App

Веб-приложение для ведения рецептов: справочники кухонь и ингредиентов, рецепты с составом и шагами приготовления, избранное и панель с метриками. Бэкенд — REST API на Django; клиент — одностраничное приложение на Vue 3.

![Заглушка превью интерфейса](https://via.placeholder.com/720x360/198754/ffffff?text=Recipe+App+%E2%80%94+Vue+%2B+Django)

*Замените изображение выше на реальный скриншот: положите файл, например `docs/screenshot.png`, и укажите относительный путь в разметке.*

---

## Стек технологий

| Слой | Технологии |
|------|------------|
| **Бэкенд** | Python, **Django 5**, **Django REST Framework**, Token Authentication, **django-filter**, SQLite |
| **Фронтенд** | **Vue.js 3** (Composition API), **Pinia**, **Vue Router**, **Vite**, **Axios**, **Bootstrap 5** + Icons |
| **База данных** | **SQLite** (файл `db.sqlite3` в корне проекта) |

---

## Системные требования

- **Python** 3.12+ (рекомендуется; совместимо с 3.10+)
- **Node.js** 20+ и **npm** (для сборки и dev-сервера фронтенда)
- Свободные порты **8000** (Django) и **5173** (Vite, по умолчанию)

---

## Установка и запуск

### Бэкенд (Django)

1. Клонируйте репозиторий и перейдите в корень проекта (где лежит `manage.py`).

2. Создайте и активируйте виртуальное окружение:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   *В Linux/macOS: `source .venv/bin/activate`*

3. Установите зависимости:

   ```bash
   pip install django djangorestframework django-filter django-cors-headers pillow
   ```

4. Примените миграции:

   ```bash
   python manage.py migrate
   ```

5. (Опционально) Создайте суперпользователя для входа в `/admin/`:

   ```bash
   python manage.py createsuperuser
   ```

6. Запустите сервер разработки:

   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

   API будет доступно по префиксу `http://127.0.0.1:8000/api/`. Медиафайлы в режиме `DEBUG` отдаются с `http://127.0.0.1:8000/media/`.

### Фронтенд (Vue 3 + Vite)

1. Перейдите в каталог `frontend/`:

   ```bash
   cd frontend
   ```

2. Установите зависимости:

   ```bash
   npm install
   ```

3. Убедитесь, что в `src/services/api.js` указан тот же хост API, что и у Django (по умолчанию `http://127.0.0.1:8000/api`). В `recipe_project/settings.py` для CORS должны быть разрешены источники фронтенда (например `http://localhost:5173`).

4. Запустите dev-сервер:

   ```bash
   npm run dev
   ```

5. Сборка для продакшена:

   ```bash
   npm run build
   ```

   Статику можно раздавать через nginx или собрать в шаблон Django — по необходимости настройте отдельно.

---

## Демо-учётные данные

В репозитории **нет** предустановленных логинов.

- **Через приложение:** откройте фронтенд → **Регистрация** → задайте `username`, `email`, `password`. После успешной регистрации вы автоматически авторизуетесь.
- **Админка Django:** после `createsuperuser` войдите на `http://127.0.0.1:8000/admin/`.

Для локальных проверок в тестах используются вымышленные пользователи (см. `recipes/tests/`); они **не** создаются при обычном `migrate`.

---

## Структура проекта

```
Cursor_Projects/                 # корень репозитория
├── manage.py
├── recipe_project/              # настройки Django (settings, urls, wsgi)
├── recipes/                     # приложение: модели, views, serializers, urls, tests/
│   └── tests/
│       ├── test_models.py
│       ├── test_views.py
│       └── test_auth.py
├── db.sqlite3                   # БД SQLite (после migrate; не коммитить в прод)
├── media/                     # загруженные файлы (обложки, фото шагов)
├── frontend/                  # SPA Vue 3
│   ├── src/
│   │   ├── components/
│   │   ├── router/
│   │   ├── services/api.js
│   │   ├── stores/            # Pinia
│   │   └── views/
│   ├── ROUTING.md             # описание маршрутов фронтенда
│   ├── STORES.md              # описание Pinia stores
│   └── package.json
└── README.md
```

---

## API endpoints (кратко)

Базовый префикс: **`/api/`**. Для защищённых ресурсов в заголовке: `Authorization: Token <ключ>`.

| Методы | Путь | Назначение |
|--------|------|------------|
| GET | `/api/health/` | Проверка живости сервиса |
| GET | `/api/statistics/` | Сводка для дашборда (только с токеном) |
| POST | `/api/auth/register/` | Регистрация → `201`, токен |
| POST | `/api/auth/login/` | Вход → `200`, токен |
| CRUD | `/api/profiles/` | Профиль текущего пользователя |
| CRUD | `/api/cuisines/` | Справочник кухонь |
| CRUD | `/api/recipes/` | Рецепты автора |
| CRUD | `/api/ingredients/` | Справочник ингредиентов |
| CRUD | `/api/recipe-ingredients/` | Состав рецептов (связь рецепт ↔ ингредиент) |
| CRUD | `/api/recipe-steps/` | Шаги приготовления |
| CRUD | `/api/favorites/` | Избранное пользователя |

Подробности полей и фильтров — в коде сериализаторов и `ViewSet` в `recipes/views.py`.

---

## Запуск тестов

Из корня проекта (с активированным venv и установленными зависимостями):

```bash
python manage.py test recipes.tests -v 2
```

Покрытие: модели (`test_models.py`), API и ViewSet (`test_views.py`), аутентификация (`test_auth.py`).

---

## Автор

Укажите своё имя или организацию при публикации репозитория.

---

## Лицензия

При необходимости добавьте файл `LICENSE` (MIT, Apache-2.0 и т.д.).
