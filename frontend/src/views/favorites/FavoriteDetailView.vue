<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFavoritesStore } from '../../stores/favorites'
import { useToastStore } from '../../stores/toast'

const props = defineProps({
  id: { type: String, required: true }
})

const router = useRouter()
const favoritesStore = useFavoritesStore()
const toast = useToastStore()

const favorite = ref(null)
const loadError = ref(false)

const recipeId = computed(() => {
  const r = favorite.value?.recipe
  if (r == null) return null
  return typeof r === 'object' && r !== null ? r.id : r
})

async function load() {
  loadError.value = false
  try {
    favorite.value = await favoritesStore.fetchOne(props.id)
  } catch (e) {
    console.error(e)
    loadError.value = true
    favorite.value = null
  }
}

function openRecipe() {
  const rid = recipeId.value
  if (rid == null) return
  router.push({ name: 'recipes-detail', params: { id: String(rid) } })
}

function editFavorite() {
  router.push({ name: 'favorites-edit', params: { id: props.id } })
}

async function deleteFavorite() {
  if (!favorite.value) return
  const title = favorite.value.recipe_title || 'запись'
  if (!confirm(`Удалить «${title}» из избранного?`)) return
  try {
    await favoritesStore.remove(props.id)
    toast.push('Удалено из избранного', 'success')
    router.push({ name: 'favorites' })
  } catch {
    /* toast из api */
  }
}

function back() {
  router.push({ name: 'favorites' })
}

onMounted(load)
</script>

<template>
  <div>
    <div v-if="loadError" class="alert alert-danger">Не удалось загрузить запись избранного.</div>

    <template v-else-if="favorite">
      <div class="d-flex flex-wrap gap-2 justify-content-between align-items-start mb-3">
        <div>
          <h1 class="h4 mb-1">Избранное</h1>
          <p class="text-muted small mb-0">ID: {{ favorite.id }}</p>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <button type="button" class="btn btn-outline-secondary btn-sm" @click="back">Назад</button>
          <button type="button" class="btn btn-primary btn-sm" @click="editFavorite">Редактировать</button>
          <button type="button" class="btn btn-outline-danger btn-sm" @click="deleteFavorite">Удалить</button>
        </div>
      </div>

      <div class="card shadow-sm">
        <div class="card-header fw-semibold">Данные</div>
        <div class="card-body">
          <dl class="row mb-4">
            <dt class="col-sm-4 text-muted">Пользователь</dt>
            <dd class="col-sm-8">{{ favorite.user_username ?? favorite.user ?? '—' }}</dd>
            <dt class="col-sm-4 text-muted">Рецепт</dt>
            <dd class="col-sm-8">
              <button type="button" class="btn btn-link p-0 align-baseline" @click="openRecipe">
                {{ favorite.recipe_title ?? (recipeId != null ? `Рецепт #${recipeId}` : '—') }}
              </button>
            </dd>
            <dt class="col-sm-4 text-muted">ID рецепта</dt>
            <dd class="col-sm-8">{{ recipeId ?? '—' }}</dd>
            <dt class="col-sm-4 text-muted">Добавлено</dt>
            <dd class="col-sm-8">{{ favorite.created_at ?? '—' }}</dd>
          </dl>

          <div class="border-top pt-3">
            <p class="fw-semibold mb-2">Связанный рецепт</p>
            <p class="text-muted small mb-2">
              Откройте карточку рецепта, чтобы увидеть описание, ингредиенты и шаги приготовления.
            </p>
            <button type="button" class="btn btn-outline-primary btn-sm" :disabled="recipeId == null" @click="openRecipe">
              Перейти к рецепту
            </button>
          </div>
        </div>
      </div>
    </template>

    <div v-else-if="favoritesStore.loading" class="text-muted py-5 text-center">Загрузка…</div>
  </div>
</template>
