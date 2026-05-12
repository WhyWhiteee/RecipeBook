<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const displayName = computed(() => authStore.user?.username || 'Пользователь')

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="d-flex min-vh-100 bg-light">
    <aside class="d-none d-lg-flex flex-column flex-shrink-0 p-3 bg-white border-end" style="width: 260px">
      <RouterLink to="/dashboard" class="d-flex align-items-center mb-4 text-decoration-none text-dark">
        <i class="bi bi-journal-bookmark me-2"></i>
        <span class="fs-5 fw-semibold">Recipe App</span>
      </RouterLink>
      <ul class="nav nav-pills flex-column gap-1">
        <li class="nav-item">
          <RouterLink class="nav-link" to="/dashboard"><i class="bi bi-speedometer2 me-2"></i>Dashboard</RouterLink>
        </li>
        <li>
          <RouterLink class="nav-link" to="/recipes"><i class="bi bi-card-list me-2"></i>Recipes</RouterLink>
        </li>
        <li>
          <RouterLink class="nav-link" to="/ingredients"><i class="bi bi-basket2 me-2"></i>Ingredients</RouterLink>
        </li>
        <li>
          <RouterLink class="nav-link" to="/cuisines"><i class="bi bi-globe2 me-2"></i>Cuisines</RouterLink>
        </li>
        <li>
          <RouterLink class="nav-link" to="/favorites"><i class="bi bi-heart me-2"></i>Favorites</RouterLink>
        </li>
      </ul>
    </aside>

    <div class="flex-grow-1 d-flex flex-column min-vh-100">
      <header class="navbar navbar-expand bg-white border-bottom px-3">
        <button
          class="btn btn-outline-secondary d-lg-none me-2"
          type="button"
          data-bs-toggle="offcanvas"
          data-bs-target="#mobileSidebar"
          aria-controls="mobileSidebar"
        >
          <i class="bi bi-list"></i>
        </button>
        <div class="ms-auto d-flex align-items-center gap-3">
          <span class="text-muted"><i class="bi bi-person-circle me-1"></i>{{ displayName }}</span>
          <button class="btn btn-outline-danger btn-sm" @click="logout">Выход</button>
        </div>
      </header>

      <main class="container-fluid p-3 p-md-4">
        <router-view />
      </main>
    </div>
  </div>

  <div class="offcanvas offcanvas-start d-lg-none" tabindex="-1" id="mobileSidebar" aria-labelledby="mobileSidebarLabel">
    <div class="offcanvas-header">
      <h5 class="offcanvas-title" id="mobileSidebarLabel">
        <i class="bi bi-journal-bookmark me-2"></i>Recipe App
      </h5>
      <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
    </div>
    <div class="offcanvas-body">
      <ul class="nav nav-pills flex-column gap-1">
        <li class="nav-item">
          <RouterLink class="nav-link" to="/dashboard" data-bs-dismiss="offcanvas">Dashboard</RouterLink>
        </li>
        <li>
          <RouterLink class="nav-link" to="/recipes" data-bs-dismiss="offcanvas">Recipes</RouterLink>
        </li>
        <li>
          <RouterLink class="nav-link" to="/ingredients" data-bs-dismiss="offcanvas">Ingredients</RouterLink>
        </li>
        <li>
          <RouterLink class="nav-link" to="/cuisines" data-bs-dismiss="offcanvas">Cuisines</RouterLink>
        </li>
        <li>
          <RouterLink class="nav-link" to="/favorites" data-bs-dismiss="offcanvas">Favorites</RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>
