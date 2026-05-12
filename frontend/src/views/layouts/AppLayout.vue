<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const auth = useAuthStore()

function onLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar navbar-expand-lg bg-white border-bottom">
    <div class="container">
      <RouterLink class="navbar-brand" to="/dashboard">Recipe App</RouterLink>
      <div class="navbar-nav gap-2">
        <RouterLink class="nav-link" to="/dashboard">Dashboard</RouterLink>
        <RouterLink class="nav-link" to="/recipes">Recipes</RouterLink>
        <RouterLink class="nav-link" to="/ingredients">Ingredients</RouterLink>
        <RouterLink class="nav-link" to="/cuisines">Cuisines</RouterLink>
        <RouterLink class="nav-link" to="/favorites">Favorites</RouterLink>
      </div>
      <button class="btn btn-outline-danger btn-sm" @click="onLogout">Logout</button>
    </div>
  </nav>
  <main class="container py-4">
    <RouterView />
  </main>
</template>
