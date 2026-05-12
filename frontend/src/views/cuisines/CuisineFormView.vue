<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCuisinesStore } from '../../stores/cuisines'
import { useToastStore } from '../../stores/toast'

const route = useRoute()
const router = useRouter()
const store = useCuisinesStore()
const toast = useToastStore()

const submitting = ref(false)

const isEdit = computed(() => route.name === 'cuisines-edit')
const entityId = computed(() => route.params.id)

const form = reactive({
  name: '',
  description: ''
})

const touched = reactive({ name: false })
const errors = reactive({ name: '' })

function validate() {
  touched.name = true
  errors.name = form.name.trim() ? '' : 'Обязательное поле'
  return !errors.name
}

async function load() {
  if (!isEdit.value) return
  const data = await store.fetchOne(entityId.value)
  form.name = data.name ?? ''
  form.description = data.description ?? ''
}

async function submit() {
  if (!validate()) return
  submitting.value = true
  try {
    const payload = {
      name: form.name.trim(),
      description: form.description
    }
    if (isEdit.value) {
      await store.update(entityId.value, payload)
    } else {
      await store.create(payload)
    }
    toast.push(isEdit.value ? 'Кухня обновлена' : 'Кухня создана', 'success')
    router.push({ name: 'cuisines' })
  } finally {
    submitting.value = false
  }
}

function cancel() {
  router.push({ name: 'cuisines' })
}

onMounted(load)
</script>

<template>
  <div class="mx-auto" style="max-width: 560px">
    <h1 class="h4 mb-4">{{ isEdit ? 'Редактирование кухни' : 'Новая кухня' }}</h1>

    <div class="card shadow-sm">
      <div class="card-body">
        <div class="mb-3">
          <label class="form-label">Название <span class="text-danger">*</span></label>
          <input
            v-model.trim="form.name"
            type="text"
            class="form-control"
            :class="{ 'is-invalid': touched.name && errors.name }"
            @blur="touched.name = true"
          />
          <div v-if="touched.name && errors.name" class="invalid-feedback d-block">{{ errors.name }}</div>
        </div>

        <div class="mb-4">
          <label class="form-label">Описание</label>
          <textarea v-model="form.description" class="form-control" rows="4"></textarea>
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
