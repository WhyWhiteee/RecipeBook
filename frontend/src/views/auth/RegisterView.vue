<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const form = reactive({
  username: '',
  email: '',
  password: '',
  password_confirm: ''
})
const submitting = ref(false)

async function submit() {
  submitting.value = true
  try {
    await auth.register(form)
    toast.push('Регистрация завершена', 'success')
    router.push('/')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center p-3">
    <div class="card shadow-sm w-100" style="max-width: 520px">
      <div class="card-body p-4">
        <h1 class="h4 mb-3 text-center">Регистрация</h1>
        <form @submit.prevent="submit">
          <div class="mb-2">
            <label class="form-label">Username</label>
            <input v-model.trim="form.username" class="form-control" autocomplete="username" required />
          </div>
          <div class="mb-2">
            <label class="form-label">Email</label>
            <input v-model.trim="form.email" type="email" class="form-control" autocomplete="email" required />
          </div>
          <div class="mb-2">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" class="form-control" autocomplete="new-password" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Confirm password</label>
            <input
              v-model="form.password_confirm"
              type="password"
              class="form-control"
              autocomplete="new-password"
              required
            />
          </div>
          <button type="submit" class="btn btn-success w-100" :disabled="submitting">
            <span v-if="submitting" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
            Зарегистрироваться
          </button>
        </form>
        <div class="text-center mt-3">
          <RouterLink to="/login">Уже есть аккаунт? Войти</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
