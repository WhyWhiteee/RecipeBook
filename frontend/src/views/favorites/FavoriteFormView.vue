<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFavoritesStore } from '../../stores/favorites'
import { useRecipesStore } from '../../stores/recipes'
import { useToastStore } from '../../stores/toast'

const route = useRoute()
const router = useRouter()
const favoritesStore = useFavoritesStore()
const recipesStore = useRecipesStore()
const toast = useToastStore()

const isEdit = computed(() => route.name === 'favorites-edit')
const entityId = computed(() => route.params.id)

const recipeOptions = ref([])
const submitting = ref(false)

const form = reactive({
  recipe: ''
})

const touched = reactive({ recipe: false })
const errors = reactive({ recipe: '' })

function validate() {
  touched.recipe = true
  errors.recipe = form.recipe ? '' : 'Выберите рецепт'
  return !errors.recipe
}

async function loadRecipes() {
  await recipesStore.fetchAll({ page_size: 500 })
  recipeOptions.value = [...recipesStore.items]
}

async function loadFavorite() {
  if (!isEdit.value) return
  const data = await favoritesStore.fetchOne(entityId.value)
  const r = data.recipe
  form.recipe = r == null ? '' : String(typeof r === 'object' && r !== null ? r.id : r)
}

async function submit() {
  if (!validate()) return
  submitting.value = true
  try {
    const payload = { recipe: Number(form.recipe) }
    if (isEdit.value) {
      await favoritesStore.update(entityId.value, payload)
    } else {
      await favoritesStore.create(payload)
    }
    toast.push(isEdit.value ? 'Избранное обновлено' : 'Добавлено в избранное', 'success')
    router.push({ name: 'favorites' })
  } finally {
    submitting.value = false
  }
}

function cancel() {
  router.push({ name: 'favorites' })
}

onMounted(async () => {
  await loadRecipes()
  await loadFavorite()
})
</script>

<template>
  <div class="mx-auto" style="max-width: 520px">
    <h1 class="h4 mb-4">{{ isEdit ? 'Изменить избранное' : 'Добавить в избранное' }}</h1>

    <div class="card shadow-sm">
      <div class="card-body">
        <div class="mb-4">
          <label class="form-label">Рецепт <span class="text-danger">*</span></label>
          <select
            v-model="form.recipe"
            class="form-select"
            :class="{ 'is-invalid': touched.recipe && errors.recipe }"
            @blur="touched.recipe = true"
          >
            <option disabled value="">— выберите рецепт —</option>
            <option v-for="r in recipeOptions" :key="r.id" :value="String(r.id)">{{ r.title }}</option>
          </select>
          <div v-if="touched.recipe && errors.recipe" class="invalid-feedback d-block">{{ errors.recipe }}</div>
        </div>

        <div class="d-flex gap-2">
          <button type="button" class="btn btn-primary" :disabled="submitting" @click="submit">
            <span v-if="submitting" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
            Сохранить
          </button>
          <button type="button" class="btn btn-outline-secondary" @click="cancel">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>
