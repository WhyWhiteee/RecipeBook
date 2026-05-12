<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import { useRecipesStore } from '../../stores/recipes'
import { useCuisinesStore } from '../../stores/cuisines'
import { useIngredientsStore } from '../../stores/ingredients'
import { useRecipeIngredientsStore } from '../../stores/recipeIngredients'
import { useRecipeStepsStore } from '../../stores/recipeSteps'
import { useToastStore } from '../../stores/toast'

const props = defineProps({
  id: { type: String, required: true }
})

const router = useRouter()
const recipesStore = useRecipesStore()
const cuisinesStore = useCuisinesStore()
const ingredientsStore = useIngredientsStore()
const recipeIngredientsStore = useRecipeIngredientsStore()
const recipeStepsStore = useRecipeStepsStore()
const toast = useToastStore()

const recipe = ref(null)
const cuisineName = ref('')
const ingredients = ref([])
const steps = ref([])
const ingredientsCatalog = ref([])
const loadError = ref(false)

const newIng = reactive({
  ingredient: '',
  quantity: '',
  unit: 'г',
  note: ''
})

const editingIngId = ref(null)
const editIng = reactive({ quantity: '', unit: '', note: '' })

const newStep = reactive({ instruction_text: '' })
const newStepFileInputKey = ref(0)
const newStepPhoto = ref(null)

const editingStepId = ref(null)
const editStep = reactive({ step_number: 1, instruction_text: '' })
const editStepPhotoInputKey = ref(0)
const editStepPhotoFile = ref(null)

const savingIng = ref(false)
const savingStep = ref(false)

const UNIT_OPTIONS = ['г', 'кг', 'мл', 'л', 'шт', 'ст. л.', 'ч. л.', 'щепотка']

const apiOrigin = 'http://127.0.0.1:8000'

function mediaUrl(path) {
  if (!path) return ''
  if (typeof path === 'string' && path.startsWith('http')) return path
  const p = typeof path === 'string' ? path : ''
  return p.startsWith('/') ? `${apiOrigin}${p}` : `${apiOrigin}/${p}`
}

const statusLabels = {
  draft: 'Черновик',
  published: 'Опубликован',
  archived: 'В архиве'
}

function ingredientFk(row) {
  const ing = row.ingredient
  return ing == null ? null : typeof ing === 'object' ? ing.id : Number(ing)
}

const availableIngredients = computed(() => {
  const used = new Set(
    ingredients.value.map((row) => ingredientFk(row)).filter((x) => x != null)
  )
  return ingredientsCatalog.value.filter((x) => !used.has(x.id))
})

const nextStepNumber = computed(() => {
  if (!steps.value.length) return 1
  return Math.max(...steps.value.map((s) => Number(s.step_number) || 0)) + 1
})

async function reloadIngredientsSteps() {
  await Promise.all([
    recipeIngredientsStore.fetchAll({ recipe: props.id, page_size: 500 }),
    recipeStepsStore.fetchAll({ recipe: props.id, page_size: 500 })
  ])
  ingredients.value = [...recipeIngredientsStore.items]
  steps.value = [...recipeStepsStore.items].sort(
    (a, b) => (a.step_number ?? 0) - (b.step_number ?? 0)
  )
}

async function load() {
  loadError.value = false
  try {
    const r = await recipesStore.fetchOne(props.id)
    recipe.value = r

    const cid = r.cuisine
    if (cid != null) {
      try {
        const c =
          typeof cid === 'object' && cid !== null
            ? cid
            : await cuisinesStore.fetchOne(typeof cid === 'number' ? cid : Number(cid))
        cuisineName.value = c?.name ?? String(cid)
      } catch {
        cuisineName.value = String(cid)
      }
    } else {
      cuisineName.value = '—'
    }

    await Promise.all([
      ingredientsStore.fetchAll({ page_size: 500 }),
      reloadIngredientsSteps()
    ])
    ingredientsCatalog.value = [...ingredientsStore.items]
  } catch (e) {
    console.error(e)
    loadError.value = true
    recipe.value = null
  }
}

async function addIngredient() {
  if (!newIng.ingredient || !String(newIng.quantity).trim()) {
    toast.push('Выберите ингредиент и укажите количество', 'danger')
    return
  }
  savingIng.value = true
  try {
    await recipeIngredientsStore.create({
      recipe: Number(props.id),
      ingredient: Number(newIng.ingredient),
      quantity: String(newIng.quantity).replace(',', '.'),
      unit: newIng.unit || 'г',
      note: newIng.note || ''
    })
    toast.push('Ингредиент добавлен', 'success')
    newIng.ingredient = ''
    newIng.quantity = ''
    newIng.unit = 'г'
    newIng.note = ''
    await reloadIngredientsSteps()
  } finally {
    savingIng.value = false
  }
}

function startEditIngredient(row) {
  editingIngId.value = row.id
  editIng.quantity = row.quantity != null ? String(row.quantity) : ''
  editIng.unit = row.unit || 'г'
  editIng.note = row.note || ''
}

function cancelEditIngredient() {
  editingIngId.value = null
}

async function saveIngredient(row) {
  savingIng.value = true
  try {
    await recipeIngredientsStore.update(row.id, {
      quantity: String(editIng.quantity).replace(',', '.'),
      unit: editIng.unit,
      note: editIng.note
    })
    toast.push('Ингредиент обновлён', 'success')
    editingIngId.value = null
    await reloadIngredientsSteps()
  } finally {
    savingIng.value = false
  }
}

async function deleteIngredient(row) {
  const name = row.ingredient_name || 'ингредиент'
  if (!confirm(`Удалить «${name}» из состава?`)) return
  savingIng.value = true
  try {
    await recipeIngredientsStore.remove(row.id)
    toast.push('Удалено из состава', 'success')
    if (editingIngId.value === row.id) editingIngId.value = null
    await reloadIngredientsSteps()
  } finally {
    savingIng.value = false
  }
}

async function addStep() {
  const text = newStep.instruction_text.trim()
  if (!text) {
    toast.push('Введите текст шага', 'danger')
    return
  }
  const n = nextStepNumber.value
  savingStep.value = true
  try {
    if (newStepPhoto.value) {
      const fd = new FormData()
      fd.append('recipe', props.id)
      fd.append('step_number', String(n))
      fd.append('instruction_text', text)
      fd.append('photo', newStepPhoto.value)
      await api.post('/recipe-steps/', fd)
    } else {
      await recipeStepsStore.create({
        recipe: Number(props.id),
        step_number: n,
        instruction_text: text
      })
    }
    toast.push('Шаг добавлен', 'success')
    newStep.instruction_text = ''
    newStepPhoto.value = null
    newStepFileInputKey.value += 1
    await reloadIngredientsSteps()
  } finally {
    savingStep.value = false
  }
}

function onNewStepPhoto(e) {
  newStepPhoto.value = e.target.files?.[0] || null
}

function startEditStep(s) {
  editingStepId.value = s.id
  editStep.step_number = Number(s.step_number) || 1
  editStep.instruction_text = s.instruction_text || ''
  editStepPhotoFile.value = null
  editStepPhotoInputKey.value += 1
}

function cancelEditStep() {
  editingStepId.value = null
}

async function saveStep(s) {
  savingStep.value = true
  try {
    if (editStepPhotoFile.value) {
      const fd = new FormData()
      fd.append('step_number', String(editStep.step_number))
      fd.append('instruction_text', editStep.instruction_text.trim())
      fd.append('photo', editStepPhotoFile.value)
      await api.patch(`/recipe-steps/${s.id}/`, fd)
    } else {
      await recipeStepsStore.update(s.id, {
        step_number: Number(editStep.step_number),
        instruction_text: editStep.instruction_text.trim()
      })
    }
    toast.push('Шаг сохранён', 'success')
    editingStepId.value = null
    await reloadIngredientsSteps()
  } finally {
    savingStep.value = false
  }
}

function onEditStepPhoto(e) {
  editStepPhotoFile.value = e.target.files?.[0] || null
}

async function deleteStep(s) {
  if (!confirm(`Удалить шаг ${s.step_number}?`)) return
  savingStep.value = true
  try {
    await recipeStepsStore.remove(s.id)
    toast.push('Шаг удалён', 'success')
    if (editingStepId.value === s.id) editingStepId.value = null
    await reloadIngredientsSteps()
  } finally {
    savingStep.value = false
  }
}

function editRecipe() {
  router.push({ name: 'recipes-edit', params: { id: props.id } })
}

async function deleteRecipe() {
  if (!recipe.value) return
  const title = recipe.value.title || `#${props.id}`
  if (!confirm(`Удалить рецепт «${title}»?`)) return
  try {
    await recipesStore.remove(props.id)
    toast.push('Рецепт удалён', 'success')
    router.push({ name: 'recipes' })
  } catch {
    /* toast из api */
  }
}

function back() {
  router.push({ name: 'recipes' })
}

onMounted(load)
</script>

<template>
  <div>
    <div v-if="loadError" class="alert alert-danger">Не удалось загрузить рецепт.</div>

    <template v-else-if="recipe">
      <div class="d-flex flex-wrap gap-2 justify-content-between align-items-start mb-3">
        <div>
          <h1 class="h4 mb-1">{{ recipe.title }}</h1>
          <p class="text-muted small mb-0">ID: {{ recipe.id }}</p>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <button type="button" class="btn btn-outline-secondary btn-sm" @click="back">Назад</button>
          <button type="button" class="btn btn-primary btn-sm" @click="editRecipe">Редактировать</button>
          <button type="button" class="btn btn-outline-danger btn-sm" @click="deleteRecipe">Удалить</button>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-lg-8">
          <div class="card shadow-sm mb-3">
            <div class="card-header fw-semibold">Основное</div>
            <div class="card-body">
              <dl class="row mb-0">
                <dt class="col-sm-4 text-muted">Автор</dt>
                <dd class="col-sm-8">{{ recipe.author_name ?? '—' }}</dd>
                <dt class="col-sm-4 text-muted">Кухня</dt>
                <dd class="col-sm-8">{{ cuisineName }}</dd>
                <dt class="col-sm-4 text-muted">Описание</dt>
                <dd class="col-sm-8" style="white-space: pre-wrap">{{ recipe.description || '—' }}</dd>
                <dt class="col-sm-4 text-muted">Подготовка</dt>
                <dd class="col-sm-8">{{ recipe.prep_time_minutes ?? 0 }} мин</dd>
                <dt class="col-sm-4 text-muted">Готовка</dt>
                <dd class="col-sm-8">{{ recipe.cook_time_minutes ?? 0 }} мин</dd>
                <dt class="col-sm-4 text-muted">Порции</dt>
                <dd class="col-sm-8">{{ recipe.servings ?? '—' }}</dd>
                <dt class="col-sm-4 text-muted">Публичный</dt>
                <dd class="col-sm-8">{{ recipe.is_public ? 'Да' : 'Нет' }}</dd>
                <dt class="col-sm-4 text-muted">Статус</dt>
                <dd class="col-sm-8">{{ statusLabels[recipe.status] ?? recipe.status }}</dd>
                <dt class="col-sm-4 text-muted">Создан</dt>
                <dd class="col-sm-8">{{ recipe.created_at ?? '—' }}</dd>
                <dt class="col-sm-4 text-muted">Обновлён</dt>
                <dd class="col-sm-8">{{ recipe.updated_at ?? '—' }}</dd>
              </dl>
            </div>
          </div>

          <div class="card shadow-sm mb-3">
            <div class="card-header fw-semibold">Ингредиенты блюда</div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-sm mb-0 align-middle">
                  <thead class="table-light">
                    <tr>
                      <th>Ингредиент</th>
                      <th style="width: 110px">Кол-во</th>
                      <th style="width: 100px">Ед.</th>
                      <th>Примечание</th>
                      <th style="width: 140px"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="!ingredients.length">
                      <td colspan="5" class="text-muted small py-3 px-3">Пока нет ингредиентов — добавьте ниже.</td>
                    </tr>
                    <tr v-for="row in ingredients" :key="row.id">
                      <template v-if="editingIngId === row.id">
                        <td>{{ row.ingredient_name ?? row.ingredient }}</td>
                        <td>
                          <input v-model="editIng.quantity" type="text" class="form-control form-control-sm" />
                        </td>
                        <td>
                          <select v-model="editIng.unit" class="form-select form-select-sm">
                            <option v-for="u in UNIT_OPTIONS" :key="u" :value="u">{{ u }}</option>
                          </select>
                        </td>
                        <td>
                          <input v-model="editIng.note" type="text" class="form-control form-control-sm" />
                        </td>
                        <td class="text-nowrap">
                          <button
                            type="button"
                            class="btn btn-sm btn-primary me-1"
                            :disabled="savingIng"
                            @click="saveIngredient(row)"
                          >
                            ОК
                          </button>
                          <button type="button" class="btn btn-sm btn-outline-secondary" @click="cancelEditIngredient">
                            Отмена
                          </button>
                        </td>
                      </template>
                      <template v-else>
                        <td>{{ row.ingredient_name ?? row.ingredient }}</td>
                        <td>{{ row.quantity ?? '—' }}</td>
                        <td>{{ row.unit ?? '—' }}</td>
                        <td>{{ row.note || '—' }}</td>
                        <td class="text-nowrap">
                          <button type="button" class="btn btn-sm btn-outline-primary me-1" @click="startEditIngredient(row)">
                            Изменить
                          </button>
                          <button
                            type="button"
                            class="btn btn-sm btn-outline-danger"
                            :disabled="savingIng"
                            @click="deleteIngredient(row)"
                          >
                            Удалить
                          </button>
                        </td>
                      </template>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="border-top p-3 bg-light">
                <div class="small fw-semibold text-muted mb-2">Добавить ингредиент</div>
                <div class="row g-2 align-items-end">
                  <div class="col-md-4">
                    <label class="form-label small mb-0">Ингредиент</label>
                    <select v-model="newIng.ingredient" class="form-select form-select-sm">
                      <option disabled value="">— выберите —</option>
                      <option v-for="opt in availableIngredients" :key="opt.id" :value="String(opt.id)">
                        {{ opt.name }}
                      </option>
                    </select>
                  </div>
                  <div class="col-md-2">
                    <label class="form-label small mb-0">Кол-во</label>
                    <input v-model="newIng.quantity" type="text" class="form-control form-control-sm" placeholder="200" />
                  </div>
                  <div class="col-md-2">
                    <label class="form-label small mb-0">Единица</label>
                    <select v-model="newIng.unit" class="form-select form-select-sm">
                      <option v-for="u in UNIT_OPTIONS" :key="u" :value="u">{{ u }}</option>
                    </select>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label small mb-0">Примечание</label>
                    <input v-model="newIng.note" type="text" class="form-control form-control-sm" placeholder="по желанию" />
                  </div>
                  <div class="col-md-1">
                    <button
                      type="button"
                      class="btn btn-sm btn-success w-100"
                      :disabled="savingIng || !availableIngredients.length"
                      @click="addIngredient"
                    >
                      <span
                        v-if="savingIng"
                        class="spinner-border spinner-border-sm"
                        aria-hidden="true"
                      ></span>
                      <span v-else>+</span>
                    </button>
                  </div>
                </div>
                <p v-if="!availableIngredients.length && ingredientsCatalog.length" class="small text-muted mb-0 mt-2">
                  Все ингредиенты из справочника уже добавлены в рецепт (или создайте новый ингредиент в разделе «Ингредиенты»).
                </p>
              </div>
            </div>
          </div>

          <div class="card shadow-sm">
            <div class="card-header fw-semibold">Шаги приготовления</div>
            <div class="card-body">
              <div v-if="!steps.length" class="text-muted small mb-3">Пока нет шагов — добавьте ниже.</div>
              <div v-for="s in steps" :key="s.id" class="border rounded p-3 mb-3">
                <template v-if="editingStepId === s.id">
                  <div class="row g-2 mb-2">
                    <div class="col-auto">
                      <label class="form-label small mb-0">№ шага</label>
                      <input
                        v-model.number="editStep.step_number"
                        type="number"
                        min="1"
                        class="form-control form-control-sm"
                        style="width: 5rem"
                      />
                    </div>
                  </div>
                  <label class="form-label small">Текст</label>
                  <textarea v-model="editStep.instruction_text" class="form-control form-control-sm mb-2" rows="3"></textarea>
                  <label class="form-label small">Новое фото шага (необязательно)</label>
                  <input
                    :key="editStepPhotoInputKey"
                    type="file"
                    class="form-control form-control-sm mb-2"
                    accept="image/*"
                    @change="onEditStepPhoto"
                  />
                  <div class="d-flex gap-2">
                    <button type="button" class="btn btn-sm btn-primary" :disabled="savingStep" @click="saveStep(s)">
                      Сохранить
                    </button>
                    <button type="button" class="btn btn-sm btn-outline-secondary" @click="cancelEditStep">Отмена</button>
                  </div>
                </template>
                <template v-else>
                  <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
                    <strong>Шаг {{ s.step_number }}</strong>
                    <div>
                      <button type="button" class="btn btn-sm btn-outline-primary me-1" @click="startEditStep(s)">
                        Изменить
                      </button>
                      <button type="button" class="btn btn-sm btn-outline-danger" :disabled="savingStep" @click="deleteStep(s)">
                        Удалить
                      </button>
                    </div>
                  </div>
                  <p class="mb-2" style="white-space: pre-wrap">{{ s.instruction_text }}</p>
                  <img
                    v-if="s.photo"
                    :src="mediaUrl(s.photo)"
                    alt=""
                    class="img-thumbnail mt-1"
                    style="max-height: 160px"
                  />
                </template>
              </div>

              <div class="border rounded p-3 bg-light">
                <div class="small fw-semibold text-muted mb-2">
                  Добавить шаг (номер {{ nextStepNumber }})
                </div>
                <textarea
                  v-model="newStep.instruction_text"
                  class="form-control form-control-sm mb-2"
                  rows="3"
                  placeholder="Опишите действие…"
                ></textarea>
                <label class="form-label small mb-1">Фото к шагу (необязательно)</label>
                <input
                  :key="newStepFileInputKey"
                  type="file"
                  class="form-control form-control-sm mb-2"
                  accept="image/*"
                  @change="onNewStepPhoto"
                />
                <button type="button" class="btn btn-sm btn-success" :disabled="savingStep" @click="addStep">
                  <span
                    v-if="savingStep"
                    class="spinner-border spinner-border-sm me-1"
                    aria-hidden="true"
                  ></span>
                  Добавить шаг
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card shadow-sm">
            <div class="card-header fw-semibold">Фото</div>
            <div class="card-body text-center">
              <img
                v-if="recipe.photo"
                :src="mediaUrl(recipe.photo)"
                class="img-fluid rounded border"
                alt=""
              />
              <span v-else class="text-muted small">Нет изображения</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else-if="recipesStore.loading" class="text-muted py-5 text-center">Загрузка…</div>
  </div>
</template>
