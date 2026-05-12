# Recipe App

Веб-приложение для ведения рецептов: справочники кухонь и ингредиентов, рецепты с составом и шагами приготовления, избранное и панель с метриками. Бэкенд — REST API на Django; клиент — одностраничное приложение на Vue 3.

![Заглушка превью интерфейса](https://via.placeholder.com/720x360/198754/ffffff?text=Recipe+App+%E2%80%94+Vue+%2B+Django)

*Замените изображение выше на реальный скриншот: положите файл, например `docs/screenshot.png`, и укажите относительный путь в разметке.*

---

## Стек технологий

| Слой | Технологии |
|------|------------|
| **Бэкенд** | Python, **Django** + **DRF**, Token Authentication, **django-filter**, **django-cors-headers**, SQLite |
| **Фронтенд** | **Vue.js 3** (Composition API), **Pinia**, **Vue Router**, **Vite**, **Axios**, **Bootstrap 5** + Icons |
| **База данных** | **SQLite** (`backend/db.sqlite3`) |

Точные версии Python-пакетов — в **`backend/requirements.txt`** (формируется через `pip freeze` после установки зависимостей).

---

## Быстрый старт «с нуля»

Из **корня репозитория** (Windows):

```bat
start.bat
```

Linux / macOS:

```bash
chmod +x start.sh
./start.sh
```

Скрипт:

1. Создаёт `backend/.venv`, ставит зависимости из `backend/requirements.txt`.
2. Выполняет `migrate`.
3. Загружает **демо-данные**: `python manage.py seed_data` (пользователи, кухни, ингредиенты, рецепты, шаги, избранное).
4. В каталоге `frontend/` выполняет `npm install` и **`npm run build`** (production-сборка).

Чтобы после `start.bat` сразу поднять серверы в отдельных окнах (Windows), задайте переменную окружения:

```bat
set RUN_SERVERS=1
start.bat
```

В Linux для запуска API + Vite preview после установки:

```bash
./start.sh --serve
```

---

## Системные требования

- **Python** 3.12+ (рекомендуется; совместимо с 3.10+)
- **Node.js** 20+ и **npm**
- Порты: **8000** (Django), **5173** (`npm run dev`), **4173** (`npm run preview` после сборки)

---

## Установка вручную

### Бэкенд

1. Перейдите в каталог **`backend/`** (там лежит `manage.py`).

2. Виртуальное окружение и зависимости:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   *Linux/macOS: `source .venv/bin/activate`*

3. Миграции и демо-данные:

   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```

4. (Опционально) Суперпользователь для `/admin/`:

   ```bash
   python manage.py createsuperuser
   ```

5. Сервер:

   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

API: `http://127.0.0.1:8000/api/`. Медиа в `DEBUG`: `http://127.0.0.1:8000/media/`.

### Фронтенд

```bash
cd frontend
npm install
npm run dev
```

Сборка: `npm run build`. Просмотр сборки: `npm run preview -- --host 127.0.0.1 --port 4173`.

В `frontend/src/services/api.js` задан базовый URL API (`http://127.0.0.1:8000/api`). В `backend/recipe_project/settings.py` в **CORS** разрешены `localhost` / `127.0.0.1` для портов **5173** и **4173**.

---

## Демо-учётные данные

После **`python manage.py seed_data`** (или **`start.bat` / `./start.sh`**) доступны пользователи (см. `backend/recipes/management/commands/seed_data.py`):

| Логин        | Пароль    |
|-------------|-----------|
| `chef_anna` | `Anna1234!` |
| `foodie_ivan` | `Ivan1234!` |
| `cook_maria`  | `Maria1234!` |

Дополнительно можно зарегистрироваться через форму во фронтенде или создать суперпользователя для админки.

---

## Структура проекта

```
Cursor_Projects/
├── start.bat                 # Windows: venv + migrate + seed_data + npm build
├── start.sh                  # Linux/macOS: то же; опция --serve
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .venv/                # локально; не коммитить
│   ├── db.sqlite3            # после migrate
│   ├── media/
│   ├── recipe_project/       # settings, urls, wsgi
│   └── recipes/              # приложение, tests, management/commands/seed_data.py
├── frontend/                 # SPA Vue 3
│   ├── src/
│   ├── ROUTING.md
│   ├── STORES.md
│   └── package.json
├── README.md
├── TZ.md
└── user_guide.md
```

---

## API endpoints (кратко)

Базовый префикс: **`/api/`**. Для защищённых ресурсов: `Authorization: Token <ключ>`.

| Методы | Путь | Назначение |
|--------|------|------------|
| GET | `/api/health/` | Проверка сервиса |
| GET | `/api/statistics/` | Сводка для дашборда |
| POST | `/api/auth/register/` | Регистрация |
| POST | `/api/auth/login/` | Вход |
| CRUD | `/api/profiles/` … `/api/favorites/` | См. TZ.md |

---

## Запуск тестов

```bash
cd backend
.venv\Scripts\activate
python manage.py test recipes.tests -v 2
```

---

## Автор

Укажите своё имя или организацию при публикации репозитория.

---

## Лицензия

При необходимости добавьте файл `LICENSE`.
