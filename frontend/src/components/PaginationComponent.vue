<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: { type: Number, required: true },
  totalPages: { type: Number, required: true }
})

const emit = defineEmits(['page-change'])

const maxNumericButtons = 7

const visiblePages = computed(() => {
  const total = Math.max(1, props.totalPages || 1)
  const cur = Math.min(Math.max(1, props.currentPage || 1), total)

  if (total <= maxNumericButtons) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  const half = Math.floor(maxNumericButtons / 2)
  let start = Math.max(1, cur - half)
  let end = Math.min(total, start + maxNumericButtons - 1)
  start = Math.max(1, end - maxNumericButtons + 1)

  const pages = []
  for (let p = start; p <= end; p++) pages.push(p)
  return pages
})

function go(page) {
  if (page < 1 || page > props.totalPages || page === props.currentPage) return
  emit('page-change', page)
}

const showPagination = computed(() => props.totalPages > 1)
</script>

<template>
  <nav v-if="showPagination" aria-label="Навигация по страницам">
    <ul class="pagination pagination-sm mb-0 flex-wrap">
      <li class="page-item" :class="{ disabled: currentPage <= 1 }">
        <button class="page-link" type="button" :disabled="currentPage <= 1" @click="go(currentPage - 1)">
          Назад
        </button>
      </li>
      <li
        v-for="p in visiblePages"
        :key="p"
        class="page-item"
        :class="{ active: p === currentPage }"
      >
        <button class="page-link" type="button" @click="go(p)">{{ p }}</button>
      </li>
      <li class="page-item" :class="{ disabled: currentPage >= totalPages }">
        <button
          class="page-link"
          type="button"
          :disabled="currentPage >= totalPages"
          @click="go(currentPage + 1)"
        >
          Вперёд
        </button>
      </li>
    </ul>
  </nav>
</template>
