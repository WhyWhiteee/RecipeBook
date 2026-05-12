<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'
import { useRecipesStore } from '../../stores/recipes'
import { useCuisinesStore } from '../../stores/cuisines'
import { useToastStore } from '../../stores/toast'

const route = useRoute()
const router = useRouter()
const recipesStore = useRecipesStore()
const cuisinesStore = useCuisinesStore()
const toast = useToastStore()

const submitting = ref(false)

const isEdit = computed(() => route.name === 'recipes-edit')
const recipeId = computed(() => route.params.id)

const cuisineOptions = ref([])
const photoFile = ref(null)

const statusChoices = [
  { value: 'draft', label: 'Черновик' },
  { value: 'published', label: 'Опубликован' },
  { value: 'archived', label: 'В архиве' }
]

const form = reactive({
  cuisine: '',
  title: '',
  description: '',
  prep_time_minutes: 0,
  cook_time_minutes: 0,
  servings: 1,
  is_public: true,
  status: 'draft'
})

const touched = reactive({
  title: false,
  status: false,
  servings: false
})

const errors = reactive({
  title: '',
  cuisine: '',
  status: '',
  servings: ''
})

function validate() {
  touched.title = true
  touched.status = true
  touched.servings = true

  errors.title = form.title.trim() ? '' : 'Обязательное поле'
  errors.status = form.status ? '' : 'Выберите статус'
  errors.servings = Number(form.servings) >= 1 ? '' : 'Минимум 1 порция'

  return !errors.title && !errors.status && !errors.servings
}

async function loadCuisines() {
  await cuisinesStore.fetchAll({ page_size: 500 })
  cuisineOptions.value = cuisinesStore.items
}

async function loadRecipe() {
  if (!isEdit.value) return
  const data = await recipesStore.fetchOne(recipeId.value)
  form.title = data.title ?? ''
  form.description = data.description ?? ''
  form.prep_time_minutes = data.prep_time_minutes ?? 0
  form.cook_time_minutes = data.cook_time_minutes ?? 0
  form.servings = data.servings ?? 1
  form.is_public = Boolean(data.is_public)
  form.status = data.status ?? 'draft'
  const c = data.cuisine
  form.cuisine =
    c == null ? '' : String(typeof c === 'object' && c !== null ? c.id : c)
}

function onPhotoChange(e) {
  const file = e.target.files?.[0]
  photoFile.value = file || null
}

async function submit() {
  if (!validate()) return

  const basePayload = {
    title: form.title.trim(),
    description: form.description,
    prep_time_minutes: Number(form.prep_time_minutes) || 0,
    cook_time_minutes: Number(form.cook_time_minutes) || 0,
    servings: Number(form.servings) || 1,
    is_public: form.is_public,
    status: form.status,
    cuisine: form.cuisine === '' ? null : Number(form.cuisine)
  }

  submitting.value = true
  try {
    if (photoFile.value) {
      const fd = new FormData()
      Object.entries(basePayload).forEach(([key, val]) => {
        if (val !== null && val !== undefined && val !== '') {
          fd.append(key, val === true ? 'true' : val === false ? 'false' : String(val))
        }
      })
      if (basePayload.cuisine === null) {
        fd.append('cuisine', '')
      }
      fd.append('photo', photoFile.value)
      if (isEdit.value) {
        await api.patch(`/recipes/${recipeId.value}/`, fd)
      } else {
        await api.post('/recipes/', fd)
      }
    } else if (isEdit.value) {
      await recipesStore.update(recipeId.value, basePayload)
    } else {
      await recipesStore.create(basePayload)
    }
    toast.push(isEdit.value ? 'Рецепт обновлён' : 'Рецепт создан', 'success')
    router.push({ name: 'recipes' })
  } finally {
    submitting.value = false
  }
}

function cancel() {
  router.push({ name: 'recipes' })
}

onMounted(async () => {
  await loadCuisines()
  await loadRecipe()
})
</script>

<template>
  <div class="mx-auto" style="max-width: 640px">
    <h1 class="h4 mb-4">{{ isEdit ? 'Редактирование рецепта' : 'Новый рецепт' }}</h1>

    <div class="card shadow-sm">
      <div class="card-body">
        <div class="mb-3">
          <label class="form-label">Название <span class="text-danger">*</span></label>
          <input
            v-model.trim="form.title"
            type="text"
            class="form-control"
            :class="{ 'is-invalid': touched.title && errors.title }"
            @blur="touched.title = true"
          />
          <div v-if="touched.title && errors.title" class="invalid-feedback d-block">{{ errors.title }}</div>
        </div>

        <div class="mb-3">
          <label class="form-label">Описание</label>
          <textarea v-model="form.description" class="form-control" rows="3"></textarea>
        </div>

        <div class="mb-3">
          <label class="form-label">Кухня</label>
          <select v-model="form.cuisine" class="form-select">
            <option value="">— не выбрано —</option>
            <option v-for="c in cuisineOptions" :key="c.id" :value="String(c.id)">{{ c.name }}</option>
          </select>
        </div>

        <div class="row">
          <div class="col-md-4 mb-3">
            <label class="form-label">Подготовка (мин)</label>
            <input v-model.number="form.prep_time_minutes" type="number" min="0" class="form-control" />
          </div>
          <div class="col-md-4 mb-3">
            <label class="form-label">Готовка (мин)</label>
            <input v-model.number="form.cook_time_minutes" type="number" min="0" class="form-control" />
          </div>
          <div class="col-md-4 mb-3">
            <label class="form-label">Порции <span class="text-danger">*</span></label>
            <input
              v-model.number="form.servings"
              type="number"
              min="1"
              class="form-control"
              :class="{ 'is-invalid': touched.servings && errors.servings }"
              @blur="touched.servings = true"
            />
            <div v-if="touched.servings && errors.servings" class="invalid-feedback d-block">{{ errors.servings }}</div>
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">Статус <span class="text-danger">*</span></label>
          <select
            v-model="form.status"
            class="form-select"
            :class="{ 'is-invalid': touched.status && errors.status }"
            @blur="touched.status = true"
          >
            <option v-for="s in statusChoices" :key="s.value" :value="s.value">{{ s.label }}</option>
          </select>
          <div v-if="touched.status && errors.status" class="invalid-feedback d-block">{{ errors.status }}</div>
        </div>

        <div class="form-check mb-3">
          <input id="recipe-public" v-model="form.is_public" type="checkbox" class="form-check-input" />
          <label class="form-check-label" for="recipe-public">Публичный</label>
        </div>

        <div class="mb-4">
          <label class="form-label">Фото</label>
          <input type="file" class="form-control" accept="image/*" @change="onPhotoChange" />
        </div>

        <div class="d-flex gap-2">
          <button type="button" class="btn btn-primary" :disabled="submitting" @click="submit">
            <span
              v-if="submitting"
              class="spinner-border spinner-border-sm me-2"
              aria-hidden="true"
            ></span>
            Сохранить
          </button>
          <button type="button" class="btn btn-outline-secondary" @click="cancel">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>
