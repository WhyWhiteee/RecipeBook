<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const loading = ref(true)
const fromApi = ref(true)
const counts = ref({
  recipes: 0,
  ingredients: 0,
  cuisines: 0,
  favorites: 0,
  recipe_steps: 0,
  recipe_ingredients: 0
})
const recipesByCuisine = ref([])
const recentRecipes = ref([])
const recentFavorites = ref([])

const statusLabels = {
  draft: 'Черновик',
  published: 'Опубликован',
  archived: 'В архиве'
}

const maxCuisineCount = computed(() =>
  recipesByCuisine.value.length ? Math.max(...recipesByCuisine.value.map((x) => x.count), 1) : 1
)

function formatDate(iso) {
  if (!iso) return '—'
  return String(iso).slice(0, 19).replace('T', ' ')
}

async function loadFromStatistics() {
  const { data } = await api.get('/statistics/', { skipErrorToast: true })
  counts.value = { ...counts.value, ...data.counts }
  recipesByCuisine.value = data.recipes_by_cuisine ?? []
  recentRecipes.value = data.recent_recipes ?? []
  recentFavorites.value = data.recent_favorites ?? []
  fromApi.value = true
}

function listResults(data) {
  if (Array.isArray(data?.results)) return data.results
  if (Array.isArray(data)) return data
  return []
}

async function loadFallback() {
  const [
    recHead,
    ingHead,
    cuiHead,
    favHead,
    stepsHead,
    riHead,
    recList,
    favList,
    cuiList
  ] = await Promise.all([
    api.get('/recipes/', { params: { page_size: 1 } }),
    api.get('/ingredients/', { params: { page_size: 1 } }),
    api.get('/cuisines/', { params: { page_size: 1 } }),
    api.get('/favorites/', { params: { page_size: 1 } }),
    api.get('/recipe-steps/', { params: { page_size: 1 } }),
    api.get('/recipe-ingredients/', { params: { page_size: 1 } }),
    api.get('/recipes/', { params: { page_size: 500, ordering: '-created_at' } }),
    api.get('/favorites/', { params: { page_size: 10, ordering: '-created_at' } }),
    api.get('/cuisines/', { params: { page_size: 500 } })
  ])

  counts.value = {
    recipes: recHead.data?.count ?? listResults(recHead.data).length,
    ingredients: ingHead.data?.count ?? listResults(ingHead.data).length,
    cuisines: cuiHead.data?.count ?? listResults(cuiHead.data).length,
    favorites: favHead.data?.count ?? listResults(favHead.data).length,
    recipe_steps: stepsHead.data?.count ?? listResults(stepsHead.data).length,
    recipe_ingredients: riHead.data?.count ?? listResults(riHead.data).length
  }

  const cuisineMap = new Map()
  for (const c of listResults(cuiList.data)) {
    cuisineMap.set(c.id, c.name)
  }

  const recipes = listResults(recList.data)
  const byKey = new Map()
  for (const r of recipes) {
    const cid = r.cuisine
    const name = cid == null ? 'Без кухни' : cuisineMap.get(cid) || `Кухня #${cid}`
    const key = cid == null ? 'null' : String(cid)
    const prev = byKey.get(key) || { cuisine_id: cid, cuisine_name: name, count: 0 }
    prev.count += 1
    byKey.set(key, prev)
  }
  recipesByCuisine.value = [...byKey.values()].sort((a, b) => b.count - a.count)

  recentRecipes.value = recipes.slice(0, 10).map((r) => ({
    id: r.id,
    title: r.title,
    status: r.status,
    created_at: r.created_at,
    cuisine_name: r.cuisine == null ? null : cuisineMap.get(r.cuisine) ?? null
  }))

  recentFavorites.value = listResults(favList.data).map((f) => ({
    id: f.id,
    created_at: f.created_at,
    recipe_title: f.recipe_title,
    recipe_id: f.recipe
  }))

  fromApi.value = false
}

async function load() {
  loading.value = true
  try {
    await loadFromStatistics()
  } catch (e) {
    console.warn('Statistics unavailable, using fallback:', e?.message || e)
    try {
      await loadFallback()
    } catch (e2) {
      console.error(e2)
    }
  } finally {
    loading.value = false
  }
}

function goRecipe(id) {
  router.push({ name: 'recipes-detail', params: { id: String(id) } })
}

function goFavoriteRecipe(row) {
  const rid = row.recipe_id ?? row.recipe
  if (rid != null) goRecipe(rid)
}

onMounted(load)
</script>

<template>
  <div>
    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-4">
      <div>
        <h1 class="h4 mb-1">Панель</h1>
        <p class="text-muted small mb-0">
          Ключевые показатели и последние записи
          <span v-if="!fromApi" class="badge text-bg-secondary ms-1">данные без /statistics/</span>
        </p>
      </div>
    </div>

    <div v-if="loading" class="d-flex justify-content-center align-items-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка…</span>
      </div>
    </div>

    <template v-else>
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card h-100 shadow-sm border-0">
            <div class="card-body">
              <div class="text-muted small">Рецепты</div>
              <div class="fs-3 fw-semibold">{{ counts.recipes }}</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card h-100 shadow-sm border-0">
            <div class="card-body">
              <div class="text-muted small">Ингредиенты</div>
              <div class="fs-3 fw-semibold">{{ counts.ingredients }}</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card h-100 shadow-sm border-0">
            <div class="card-body">
              <div class="text-muted small">Кухни</div>
              <div class="fs-3 fw-semibold">{{ counts.cuisines }}</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card h-100 shadow-sm border-0">
            <div class="card-body">
              <div class="text-muted small">Избранное</div>
              <div class="fs-3 fw-semibold">{{ counts.favorites }}</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card h-100 shadow-sm border-0">
            <div class="card-body">
              <div class="text-muted small">Шаги рецептов</div>
              <div class="fs-3 fw-semibold">{{ counts.recipe_steps }}</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-4 col-xl-2">
          <div class="card h-100 shadow-sm border-0">
            <div class="card-body">
              <div class="text-muted small">Состав блюд</div>
              <div class="fs-3 fw-semibold">{{ counts.recipe_ingredients }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-lg-6">
          <div class="card shadow-sm h-100">
            <div class="card-header fw-semibold">Рецепты по кухням</div>
            <div class="card-body">
              <p v-if="!recipesByCuisine.length" class="text-muted small mb-0">Нет данных для распределения.</p>
              <div v-else>
                <div v-for="row in recipesByCuisine" :key="String(row.cuisine_id ?? 'none')" class="mb-3">
                  <div class="d-flex justify-content-between small mb-1">
                    <span>{{ row.cuisine_name }}</span>
                    <span class="text-muted">{{ row.count }}</span>
                  </div>
                  <div class="progress" style="height: 8px">
                    <div
                      class="progress-bar"
                      role="progressbar"
                      :style="{ width: `${(row.count / maxCuisineCount) * 100}%` }"
                      :aria-valuenow="row.count"
                      aria-valuemin="0"
                      :aria-valuemax="maxCuisineCount"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-6">
          <div class="card shadow-sm h-100">
            <div class="card-header fw-semibold d-flex justify-content-between align-items-center">
              <span>Последние рецепты</span>
              <RouterLink to="/recipes" class="small">Все</RouterLink>
            </div>
            <div class="card-body p-0">
              <div v-if="!recentRecipes.length" class="p-3 text-muted small">Пока нет рецептов.</div>
              <ul v-else class="list-group list-group-flush">
                <li
                  v-for="r in recentRecipes"
                  :key="r.id"
                  class="list-group-item list-group-item-action py-2"
                  role="button"
                  @click="goRecipe(r.id)"
                >
                  <div class="d-flex justify-content-between gap-2">
                    <span class="fw-medium text-truncate">{{ r.title }}</span>
                    <span class="text-muted small text-nowrap">{{ statusLabels[r.status] ?? r.status }}</span>
                  </div>
                  <div class="small text-muted">
                    {{ r.cuisine_name || '—' }} · {{ formatDate(r.created_at) }}
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-12">
          <div class="card shadow-sm">
            <div class="card-header fw-semibold d-flex justify-content-between align-items-center">
              <span>Последнее избранное</span>
              <RouterLink to="/favorites" class="small">Все</RouterLink>
            </div>
            <div class="card-body p-0">
              <div v-if="!recentFavorites.length" class="p-3 text-muted small">Записей нет.</div>
              <div v-else class="table-responsive">
                <table class="table table-hover table-sm mb-0 align-middle">
                  <thead class="table-light">
                    <tr>
                      <th>Рецепт</th>
                      <th>Добавлено</th>
                      <th style="width: 120px"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="f in recentFavorites" :key="f.id">
                      <td>{{ f.recipe_title || '—' }}</td>
                      <td class="text-muted small">{{ formatDate(f.created_at) }}</td>
                      <td>
                        <button
                          type="button"
                          class="btn btn-link btn-sm py-0"
                          :disabled="f.recipe_id == null && f.recipe == null"
                          @click="goFavoriteRecipe(f)"
                        >
                          Открыть рецепт
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
