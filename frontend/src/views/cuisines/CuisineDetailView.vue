<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCuisinesStore } from '../../stores/cuisines'
import { useRecipesStore } from '../../stores/recipes'
import { useToastStore } from '../../stores/toast'

const props = defineProps({
  id: { type: String, required: true }
})

const router = useRouter()
const cuisinesStore = useCuisinesStore()
const recipesStore = useRecipesStore()
const toast = useToastStore()

const cuisine = ref(null)
const recipes = ref([])
const loadError = ref(false)

const statusLabels = {
  draft: 'Черновик',
  published: 'Опубликован',
  archived: 'В архиве'
}

async function load() {
  loadError.value = false
  try {
    const data = await cuisinesStore.fetchOne(props.id)
    cuisine.value = data
    await recipesStore.fetchAll({ cuisine: props.id, page_size: 500 })
    recipes.value = [...recipesStore.items]
  } catch (e) {
    console.error(e)
    loadError.value = true
    cuisine.value = null
  }
}

function goRecipe(item) {
  router.push({ name: 'recipes-detail', params: { id: String(item.id) } })
}

function editCuisine() {
  router.push({ name: 'cuisines-edit', params: { id: props.id } })
}

async function deleteCuisine() {
  if (!cuisine.value) return
  const name = cuisine.value.name || `#${props.id}`
  if (!confirm(`Удалить кухню «${name}»?`)) return
  try {
    await cuisinesStore.remove(props.id)
    toast.push('Кухня удалена', 'success')
    router.push({ name: 'cuisines' })
  } catch {
    /* toast из api */
  }
}

function back() {
  router.push({ name: 'cuisines' })
}

onMounted(load)
</script>

<template>
  <div>
    <div v-if="loadError" class="alert alert-danger">Не удалось загрузить кухню.</div>

    <template v-else-if="cuisine">
      <div class="d-flex flex-wrap gap-2 justify-content-between align-items-start mb-3">
        <div>
          <h1 class="h4 mb-1">{{ cuisine.name }}</h1>
          <p class="text-muted small mb-0">ID: {{ cuisine.id }}</p>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <button type="button" class="btn btn-outline-secondary btn-sm" @click="back">Назад</button>
          <button type="button" class="btn btn-primary btn-sm" @click="editCuisine">Редактировать</button>
          <button type="button" class="btn btn-outline-danger btn-sm" @click="deleteCuisine">Удалить</button>
        </div>
      </div>

      <div class="card shadow-sm mb-3">
        <div class="card-header fw-semibold">Поля</div>
        <div class="card-body">
          <dl class="row mb-0">
            <dt class="col-sm-4 text-muted">Название</dt>
            <dd class="col-sm-8">{{ cuisine.name }}</dd>
            <dt class="col-sm-4 text-muted">Описание</dt>
            <dd class="col-sm-8" style="white-space: pre-wrap">{{ cuisine.description || '—' }}</dd>
          </dl>
        </div>
      </div>

      <div class="card shadow-sm">
        <div class="card-header fw-semibold">Рецепты этой кухни</div>
        <div class="card-body p-0">
          <div v-if="!recipes.length" class="p-3 text-muted small">Рецептов пока нет.</div>
          <div v-else class="table-responsive">
            <table class="table table-hover table-sm mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>Название</th>
                  <th>Статус</th>
                  <th>Публичный</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in recipes" :key="r.id" role="button" @click="goRecipe(r)">
                  <td>{{ r.title }}</td>
                  <td>{{ statusLabels[r.status] ?? r.status }}</td>
                  <td>{{ r.is_public ? 'Да' : 'Нет' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>

    <div v-else-if="cuisinesStore.loading" class="text-muted py-5 text-center">Загрузка…</div>
  </div>
</template>
