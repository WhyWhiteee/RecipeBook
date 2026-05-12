import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const items = ref([])
  let seq = 0

  function push(message, variant = 'success') {
    seq += 1
    items.value.push({ id: seq, message: String(message), variant })
    return seq
  }

  function remove(id) {
    items.value = items.value.filter((t) => t.id !== id)
  }

  return { items, push, remove }
})
