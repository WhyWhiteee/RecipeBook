<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useIngredientsStore } from '../../stores/ingredients'
import { useRecipeIngredientsStore } from '../../stores/recipeIngredients'
import { useToastStore } from '../../stores/toast'

const props = defineProps({
  id: { type: String, required: true }
})

const router = useRouter()
const ingredientsStore = useIngredientsStore()
const recipeIngredientsStore = useRecipeIngredientsStore()
const toast = useToastStore()

const ingredient = ref(null)
const usages = ref([])
const loadError = ref(false)

async function load() {
  loadError.value = false
  try {
    const data = await ingredientsStore.fetchOne(props.id)
    ingredient.value = data
    await recipeIngredientsStore.fetchAll({ ingredient: props.id, page_size: 500 })
    usages.value = [...recipeIngredientsStore.items]
  } catch (e) {
    console.error(e)
    loadError.value = true
    ingredient.value = null
  }
}

function goRecipe(rid) {
  const id = typeof rid === 'object' && rid !== null ? rid.id : rid
  if (id == null) return
  router.push({ name: 'recipes-detail', params: { id: String(id) } })
}

function editIngredient() {
  router.push({ name: 'ingredients-edit', params: { id: props.id } })
}

async function deleteIngredient() {
  if (!ingredient.value) return
  const name = ingredient.value.name || `#${props.id}`
  if (!confirm(`Удалить ингредиент «${name}»?`)) return
  try {
    await ingredientsStore.remove(props.id)
    toast.push('Ингредиент удалён', 'success')
    router.push({ name: 'ingredients' })
  } catch {
    /* toast из api */
  }
}

function back() {
  router.push({ name: 'ingredients' })
}

onMounted(load)
</script>

<template>
  <div>
    <div v-if="loadError" class="alert alert-danger">Не удалось загрузить ингредиент.</div>

    <template v-else-if="ingredient">
      <div class="d-flex flex-wrap gap-2 justify-content-between align-items-start mb-3">
        <div>
          <h1 class="h4 mb-1">{{ ingredient.name }}</h1>
          <p class="text-muted small mb-0">ID: {{ ingredient.id }}</p>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <button type="button" class="btn btn-outline-secondary btn-sm" @click="back">Назад</button>
          <button type="button" class="btn btn-primary btn-sm" @click="editIngredient">Редактировать</button>
          <button type="button" class="btn btn-outline-danger btn-sm" @click="deleteIngredient">Удалить</button>
        </div>
      </div>

      <div class="card shadow-sm mb-3">
        <div class="card-header fw-semibold">Поля</div>
        <div class="card-body">
          <dl class="row mb-0">
            <dt class="col-sm-4 text-muted">Название</dt>
            <dd class="col-sm-8">{{ ingredient.name }}</dd>
            <dt class="col-sm-4 text-muted">Создан</dt>
            <dd class="col-sm-8">{{ ingredient.created_at ?? '—' }}</dd>
          </dl>
        </div>
      </div>

      <div class="card shadow-sm">
        <div class="card-header fw-semibold">Использование в рецептах</div>
        <div class="card-body p-0">
          <div v-if="!usages.length" class="p-3 text-muted small">Ингредиент ни в одном рецепте не указан.</div>
          <div v-else class="table-responsive">
            <table class="table table-hover table-sm mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>Рецепт</th>
                  <th>Кол-во</th>
                  <th>Ед.</th>
                  <th>Примечание</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in usages" :key="row.id" role="button" @click="goRecipe(row.recipe)">
                  <td>{{ row.recipe_title ?? row.recipe }}</td>
                  <td>{{ row.quantity ?? '—' }}</td>
                  <td>{{ row.unit ?? '—' }}</td>
                  <td>{{ row.note || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>

    <div v-else-if="ingredientsStore.loading" class="text-muted py-5 text-center">Загрузка…</div>
  </div>
</template>
