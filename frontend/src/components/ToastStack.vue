<script setup>
import { useToastStore } from '../stores/toast'
import ToastItem from './ToastItem.vue'

const toastStore = useToastStore()

function onClose(id) {
  toastStore.remove(id)
}
</script>

<template>
  <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1085">
    <ToastItem
      v-for="t in toastStore.items"
      :key="t.id"
      :message="t.message"
      :variant="t.variant"
      @close="onClose(t.id)"
    />
  </div>
</template>
