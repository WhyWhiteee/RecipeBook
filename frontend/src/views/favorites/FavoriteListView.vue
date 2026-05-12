<script setup>
import { onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import PaginationComponent from '../../components/PaginationComponent.vue'
import { useFavoritesStore } from '../../stores/favorites'
import { useRecipesStore } from '../../stores/recipes'
import { useToastStore } from '../../stores/toast'

const router = useRouter()
const store = useFavoritesStore()
const recipesStore = useRecipesStore()
const toast = useToastStore()

const recipeOptions = ref([])

const ui = reactive({
  page: 1,
  search: '',
  recipe: '',
  ordering: ''
})

const orderingOptions = [
  { label: 'Сначала новые', value: '' },
  { label: 'Сначала старые', value: 'created_at' },
  { label: 'ID ↑', value: 'id' },
  { label: 'ID ↓', value: '-id' }
]

function buildParams() {
  return {
    page: ui.page,
    search: ui.search.trim() || undefined,
    recipe: ui.recipe || undefined,
    ordering: ui.ordering || undefined
  }
}

async function loadData() {
  await store.fetchAll(buildParams())
}

function resetFilters() {
  ui.search = ''
  ui.recipe = ''
  ui.ordering = ''
  ui.page = 1
  loadData()
}

function onRecipeChange() {
  ui.page = 1
  loadData()
}

function onOrderingChange() {
  ui.page = 1
  loadData()
}

let searchDebounce = null
watch(
  () => ui.search,
  () => {
    clearTimeout(searchDebounce)
    searchDebounce = setTimeout(() => {
      ui.page = 1
      loadData()
    }, 300)
  }
)

onBeforeUnmount(() => clearTimeout(searchDebounce))

function goToDetails(item) {
  router.push({ name: 'favorites-detail', params: { id: String(item.id) } })
}

function onEdit(item) {
  router.push(`/favorites/${item.id}/edit`)
}

async function onDelete(item) {
  if (!confirm(`Убрать «${item.recipe_title}» из избранного?`)) return
  try {
    await store.remove(item.id)
    toast.push('Запись удалена из избранного', 'success')
    await loadData()
  } catch {
    /* toast из api */
  }
}

async function changePage(page) {
  if (page < 1 || page > store.totalPages) return
  ui.page = page
  await loadData()
}

onMounted(async () => {
  await recipesStore.fetchAll({ page_size: 500, ordering: 'title' })
  recipeOptions.value = recipesStore.items
  await loadData()
})
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h4 mb-0">Избранное</h1>
      <RouterLink class="btn btn-primary btn-sm" to="/favorites/create">Создать</RouterLink>
    </div>

    <div class="card shadow-sm mb-3">
      <div class="card-body py-3">
        <div class="row g-2 align-items-end">
          <div class="col-12 col-md-3">
            <label class="form-label small text-muted mb-1">Порядок</label>
            <select v-model="ui.ordering" class="form-select form-select-sm" @change="onOrderingChange">
              <option v-for="opt in orderingOptions" :key="opt.value || 'def'" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
          <div class="col-12 col-md-3">
            <label class="form-label small text-muted mb-1">Рецепт</label>
            <select v-model="ui.recipe" class="form-select form-select-sm" @change="onRecipeChange">
              <option value="">Все рецепты</option>
              <option v-for="r in recipeOptions" :key="r.id" :value="String(r.id)">{{ r.title }}</option>
            </select>
          </div>
          <div class="col-12 col-md-4">
            <label class="form-label small text-muted mb-1">Поиск</label>
            <input
              v-model.trim="ui.search"
              type="search"
              class="form-control form-control-sm"
              placeholder="Название рецепта, пользователь…"
              autocomplete="off"
            />
          </div>
          <div class="col-12 col-md-2">
            <button type="button" class="btn btn-outline-secondary btn-sm w-100" @click="resetFilters">
              Сбросить
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="position-relative rounded border bg-white" style="min-height: 200px">
      <div class="table-responsive" :class="{ 'opacity-50': store.loading }">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Рецепт</th>
              <th>Пользователь</th>
              <th>Создано</th>
              <th style="width: 180px">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!store.loading && !store.items.length">
              <td colspan="5" class="text-center py-4 text-muted">Нет данных</td>
            </tr>
            <tr v-for="item in store.items" :key="item.id" role="button" @click="goToDetails(item)">
              <td>{{ item.id }}</td>
              <td>{{ item.recipe_title }}</td>
              <td>{{ item.user_username }}</td>
              <td>{{ item.created_at?.slice(0, 10) }}</td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-2" @click.stop="onEdit(item)">Редактировать</button>
                <button class="btn btn-sm btn-outline-danger" @click.stop="onDelete(item)">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div
        v-if="store.loading"
        class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center rounded bg-white bg-opacity-75"
      >
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка…</span>
        </div>
      </div>
    </div>

    <div class="mt-3">
      <PaginationComponent
        :current-page="ui.page"
        :total-pages="store.totalPages"
        @page-change="changePage"
      />
    </div>
  </div>
</template>
