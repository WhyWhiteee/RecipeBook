<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { Toast } from 'bootstrap'

const props = defineProps({
  message: { type: String, required: true },
  variant: { type: String, default: 'success' }
})

const emit = defineEmits(['close'])

const root = ref(null)
let instance

function onHidden() {
  emit('close')
}

onMounted(() => {
  const el = root.value
  instance = Toast.getOrCreateInstance(el, { autohide: true, delay: 3000 })
  el.addEventListener('hidden.bs.toast', onHidden)
  instance.show()
})

onBeforeUnmount(() => {
  root.value?.removeEventListener('hidden.bs.toast', onHidden)
})
</script>

<template>
  <div
    ref="root"
    class="toast align-items-center border-0"
    :class="variant === 'danger' ? 'text-bg-danger' : 'text-bg-success'"
    role="alert"
    aria-live="polite"
    aria-atomic="true"
  >
    <div class="d-flex">
      <div class="toast-body">{{ message }}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Закрыть" />
    </div>
  </div>
</template>
