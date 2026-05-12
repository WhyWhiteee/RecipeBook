<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' }
})

const emit = defineEmits(['delete'])
</script>

<template>
  <article class="recipe-card card">
    <div class="card-body">
      <h3 class="card-title">{{ title }}</h3>
      <p v-if="subtitle" class="card-subtitle text-muted mb-2">{{ subtitle }}</p>
      <button
        type="button"
        class="btn btn-outline-danger btn-delete"
        data-testid="delete-recipe"
        @click="emit('delete')"
      >
        Удалить
      </button>
    </div>
  </article>
</template>
