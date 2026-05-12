<script setup>
import { onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import PaginationComponent from '../../components/PaginationComponent.vue'
import { useRecipesStore } from '../../stores/recipes'
import { useCuisinesStore } from '../../stores/cuisines'
import { useToastStore } from '../../stores/toast'

const router = useRouter()
const store = useRecipesStore()
const cuisinesStore = useCuisinesStore()
const toast = useToastStore()

const cuisineOptions = ref([])

const ui = reactive({
  page: 1,
  search: '',
  cuisine: '',
  status: ''
})

const statusOptions = [
  { label: 'Все статусы', value: '' },
  { label: 'Черновик', value: 'draft' },
  { label: 'Опубликован', value: 'published' },
  { label: 'В архиве', value: 'archived' }
]

function buildParams() {
  return {
    page: ui.page,
    search: ui.search.trim() || undefined,
    cuisine: ui.cuisine || undefined,
    status: ui.status || undefined
  }
}

async function loadData() {
  await store.fetchAll(buildParams())
}

function resetFilters() {
  ui.search = ''
  ui.cuisine = ''
  ui.status = ''
  ui.page = 1
  loadData()
}

function onFilterChange() {
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
  router.push(`/recipes/${item.id}`)
}

function onEdit(item) {
  router.push(`/recipes/${item.id}/edit`)
}

async function onDelete(item) {
  if (!confirm(`Удалить рецепт «${item.title}»?`)) return
  try {
    await store.remove(item.id)
    toast.push('Рецепт удалён', 'success')
    await loadData()
  } catch {
    /* ошибка — toast из api */
  }
}

async function changePage(page) {
  if (page < 1 || page > store.totalPages) return
  ui.page = page
  await loadData()
}

onMounted(async () => {
  await cuisinesStore.fetchAll({ page_size: 500 })
  cuisineOptions.value = cuisinesStore.items
  await loadData()
})
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h4 mb-0">Рецепты</h1>
      <RouterLink class="btn btn-primary btn-sm" to="/recipes/create">Создать</RouterLink>
    </div>

    <div class="card shadow-sm mb-3">
      <div class="card-body py-3">
        <div class="row g-2 align-items-end">
          <div class="col-12 col-md-3">
            <label class="form-label small text-muted mb-1">Кухня</label>
            <select v-model="ui.cuisine" class="form-select form-select-sm" @change="onFilterChange">
              <option value="">Все кухни</option>
              <option v-for="c in cuisineOptions" :key="c.id" :value="String(c.id)">{{ c.name }}</option>
            </select>
          </div>
          <div class="col-12 col-md-3">
            <label class="form-label small text-muted mb-1">Статус</label>
            <select v-model="ui.status" class="form-select form-select-sm" @change="onFilterChange">
              <option v-for="opt in statusOptions" :key="opt.value || 'all'" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
          <div class="col-12 col-md-4">
            <label class="form-label small text-muted mb-1">Поиск</label>
            <input
              v-model.trim="ui.search"
              type="search"
              class="form-control form-control-sm"
              placeholder="Название, описание…"
              autocomplete="off"
            />
          </div>
          <div class="col-12 col-md-2">
            <button type="button" class="btn btn-outline-secondary btn-sm w-100" @click="resetFilters">
              Сбросить фильтры
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
              <th>Название</th>
              <th>Статус</th>
              <th>Публичный</th>
              <th>Порции</th>
              <th>Создан</th>
              <th style="width: 180px">Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!store.loading && !store.items.length">
              <td colspan="7" class="text-center py-4 text-muted">Нет данных</td>
            </tr>
            <tr v-for="item in store.items" :key="item.id" role="button" @click="goToDetails(item)">
              <td>{{ item.id }}</td>
              <td>{{ item.title }}</td>
              <td>{{ item.status }}</td>
              <td>{{ item.is_public ? 'Да' : 'Нет' }}</td>
              <td>{{ item.servings }}</td>
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
