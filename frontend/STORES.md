# Pinia stores — описание

Файлы лежат в `src/stores/`. Подключение: `app.use(createPinia())` в `main.js`.

- **`auth`** — синтаксис **Options API** (`state` / `getters` / `actions`).
- Остальные ресурсные сторы и **`toast`** — **Setup Stores** (`defineStore(id, () => { ... return { ... } })`): вместо отдельных **getters** используются обычные `ref`/`computed` внутри setup и возвращаются наружу; явных геттеров в коде нет.

Ниже для каждого стора: **state**, **getters**, **actions**. Для Setup-сторов в колонке state перечислены возвращаемые реактивные поля.

---

## `useAuthStore` — `auth`

| Роль | Содержимое |
|------|------------|
| **Файл** | `stores/auth.js` |
| **API** | `/auth/login/`, `/auth/register/` |
| **State** | `token` — строка токена или `null` (дублируется с `localStorage`); `user` — объект `{ id, username, email }` или `null` после выхода |
| **Getters** | `isAuthenticated` — `boolean`, есть ли непустой `token` |
| **Actions** | `login(payload)` — POST логин, сохраняет токен и пользователя; `register(payload)` — POST регистрация, то же; `logout()` — очищает состояние и `localStorage` |

---

## `useToastStore` — `toast`

| Роль | Содержимое |
|------|------------|
| **Файл** | `stores/toast.js` |
| **State** | `items` — массив `{ id, message, variant }` (очередь уведомлений для `ToastStack`) |
| **Getters** | нет |
| **Actions** | `push(message, variant)` — добавить toast (`variant`: `'success'` \| `'danger'`, по умолчанию success); `remove(id)` — убрать элемент после скрытия |

---

## `useRecipesStore` — `recipes`

| Роль | Содержимое |
|------|------------|
| **Файл** | `stores/recipes.js` |
| **API** | `/recipes/` |
| **State** | `items` — список рецептов (последний ответ `fetchAll`); `currentItem` — объект последнего `fetchOne`; `loading` — флаг запроса; `totalPages` — расчёт по `count` и `page_size`; `filters` — накопленные query-параметры для списка (мержатся при каждом `fetchAll`) |
| **Getters** | нет |
| **Actions** | `fetchAll(params?)` — GET список; `fetchOne(id)` — GET один; `create(payload)` — POST; `update(id, payload)` — PATCH; `remove(id)` — DELETE |

---

## `useIngredientsStore` — `ingredients`

| Роль | Содержимое |
|------|------------|
| **Файл** | `stores/ingredients.js` |
| **API** | `/ingredients/` |
| **State** | то же паттерн: `items`, `currentItem`, `loading`, `totalPages`, `filters` |
| **Getters** | нет |
| **Actions** | `fetchAll`, `fetchOne`, `create`, `update`, `remove` |

---

## `useCuisinesStore` — `cuisines`

| Роль | Содержимое |
|------|------------|
| **Файл** | `stores/cuisines.js` |
| **API** | `/cuisines/` |
| **State** | `items`, `currentItem`, `loading`, `totalPages`, `filters` |
| **Getters** | нет |
| **Actions** | `fetchAll`, `fetchOne`, `create`, `update`, `remove` |

---

## `useFavoritesStore` — `favorites`

| Роль | Содержимое |
|------|------------|
| **Файл** | `stores/favorites.js` |
| **API** | `/favorites/` |
| **State** | `items`, `currentItem`, `loading`, `totalPages`, `filters` |
| **Getters** | нет |
| **Actions** | `fetchAll`, `fetchOne`, `create`, `update`, `remove` |

---

## `useProfilesStore` — `profiles`

| Роль | Содержимое |
|------|------------|
| **Файл** | `stores/profiles.js` |
| **API** | `/profiles/` (на бэкенде выборка обычно только профиль текущего пользователя) |
| **State** | `items`, `currentItem`, `loading`, `totalPages`, `filters` |
| **Getters** | нет |
| **Actions** | `fetchAll`, `fetchOne`, `create`, `update`, `remove` |

*В текущем UI может быть не подключён; стор готов для экранов профиля.*

---

## `useRecipeIngredientsStore` — `recipeIngredients`

| Роль | Содержимое |
|------|------------|
| **Файл** | `stores/recipeIngredients.js` |
| **API** | `/recipe-ingredients/` |
| **State** | `items`, `currentItem`, `loading`, `totalPages`, `filters` |
| **Getters** | нет |
| **Actions** | `fetchAll`, `fetchOne`, `create`, `update`, `remove` |

---

## `useRecipeStepsStore` — `recipeSteps`

| Роль | Содержимое |
|------|------------|
| **Файл** | `stores/recipeSteps.js` |
| **API** | `/recipe-steps/` |
| **State** | `items`, `currentItem`, `loading`, `totalPages`, `filters` |
| **Getters** | нет |
| **Actions** | `fetchAll`, `fetchOne`, `create`, `update`, `remove` |

---

## Общие замечания по ресурсным сторам

1. **`fetchAll`** объединяет переданные `params` с предыдущим `filters` (`{ ...filters.value, ...params }`), поэтому параметры списка накапливаются, пока не перезапишутся тем же ключом.
2. **`totalPages`** считается от ответа DRF (`count` / `page_size`); при ответе без пагинации возможно значение `1` или `0` в зависимости от данных.
3. Ошибки пробрасываются наружу (`throw`); глобально их может обрабатывать перехватчик в `services/api.js` (toast).
4. Загрузка файлов (например фото шага) в части мест обходит стор и идёт через `api.post` / `api.patch` с `FormData` — см. `RecipeFormView`, `RecipeDetailView`.
