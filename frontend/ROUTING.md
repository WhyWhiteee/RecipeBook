# Маршрутизация приложения

История: HTML5 History (`createWebHistory`). Корень `/` использует `MainLayout` (боковая панель + шапка), кроме явных редиректов.

**Защита:** маршруты без `meta.public` требуют токен в `localStorage`; иначе редирект на `/login?redirect=…`. Публичные (`/login`, `/register`) при уже авторизованном пользователе ведут на дашборд.

## Таблица маршрутов

| Path | name | Component (файл) | Описание |
|------|------|------------------|----------|
| `/login` | `login` | `views/auth/LoginView.vue` | Страница входа (публичная) |
| `/register` | `register` | `views/auth/RegisterView.vue` | Регистрация (публичная) |
| `/` | — | — | Редирект на `/dashboard` |
| `/dashboard` | `dashboard` | `views/DashboardView.vue` | Панель: метрики, статистика, последние записи |
| `/recipes` | `recipes` | `views/recipes/RecipeListView.vue` | Список рецептов пользователя |
| `/recipes/create` | `recipes-create` | `views/recipes/RecipeFormView.vue` | Создание рецепта |
| `/recipes/:id/edit` | `recipes-edit` | `views/recipes/RecipeFormView.vue` | Редактирование рецепта (`id` в params) |
| `/recipes/:id` | `recipes-detail` | `views/recipes/RecipeDetailView.vue` | Карточка рецепта, состав, шаги (`props: id`) |
| `/ingredients` | `ingredients` | `views/ingredients/IngredientListView.vue` | Справочник ингредиентов |
| `/ingredients/create` | `ingredients-create` | `views/ingredients/IngredientFormView.vue` | Новый ингредиент |
| `/ingredients/:id/edit` | `ingredients-edit` | `views/ingredients/IngredientFormView.vue` | Редактирование ингредиента |
| `/ingredients/:id` | `ingredients-detail` | `views/ingredients/IngredientDetailView.vue` | Карточка ингредиента (`props: id`) |
| `/cuisines` | `cuisines` | `views/cuisines/CuisineListView.vue` | Список кухонь |
| `/cuisines/create` | `cuisines-create` | `views/cuisines/CuisineFormView.vue` | Новая кухня |
| `/cuisines/:id/edit` | `cuisines-edit` | `views/cuisines/CuisineFormView.vue` | Редактирование кухни |
| `/cuisines/:id` | `cuisines-detail` | `views/cuisines/CuisineDetailView.vue` | Карточка кухни (`props: id`) |
| `/favorites` | `favorites` | `views/favorites/FavoriteListView.vue` | Список избранного |
| `/favorites/create` | `favorites-create` | `views/favorites/FavoriteFormView.vue` | Добавить рецепт в избранное |
| `/favorites/:id/edit` | `favorites-edit` | `views/favorites/FavoriteFormView.vue` | Редактирование записи избранного |
| `/favorites/:id` | `favorites-detail` | `views/favorites/FavoriteDetailView.vue` | Карточка записи избранного (`props: id`) |

## Обертка макета

| Узел | Component | Описание |
|------|-----------|----------|
| Родитель `/` | `views/layouts/MainLayout.vue` | Общий layout: сайдбар, шапка, `<router-view />` для дочерних маршрутов |

Компоненты подключаются **лениво** (`() => import(...)`) в `src/router/index.js`.

## Порядок объявления (важно для Vue Router)

Статические сегменты (`create`, `edit`) объявлены **выше** динамических `:id`, чтобы URL вроде `/recipes/5/edit` не обрабатывался как `recipes-detail` с `id = "5/edit"`.
