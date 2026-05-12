<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const form = reactive({ username: '', password: '' })
const submitting = ref(false)

async function submit() {
  submitting.value = true
  try {
    await auth.login(form)
    toast.push('Вход выполнен', 'success')
    router.push('/')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center p-3">
    <div class="card shadow-sm w-100" style="max-width: 420px">
      <div class="card-body p-4">
        <h1 class="h4 mb-3 text-center">Вход</h1>
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Username</label>
            <input v-model.trim="form.username" class="form-control" autocomplete="username" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input
              v-model="form.password"
              type="password"
              class="form-control"
              autocomplete="current-password"
              required
            />
          </div>
          <button type="submit" class="btn btn-primary w-100" :disabled="submitting">
            <span v-if="submitting" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
            Войти
          </button>
        </form>
        <div class="text-center mt-3">
          <RouterLink to="/register">Нет аккаунта? Регистрация</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
