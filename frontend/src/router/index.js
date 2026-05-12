import { createRouter, createWebHistory } from 'vue-router'

const LoginView = () => import('../views/auth/LoginView.vue')
const RegisterView = () => import('../views/auth/RegisterView.vue')
const MainLayout = () => import('../views/layouts/MainLayout.vue')
const DashboardView = () => import('../views/DashboardView.vue')

const RecipeListView = () => import('../views/recipes/RecipeListView.vue')
const RecipeDetailView = () => import('../views/recipes/RecipeDetailView.vue')
const RecipeFormView = () => import('../views/recipes/RecipeFormView.vue')

const IngredientListView = () => import('../views/ingredients/IngredientListView.vue')
const IngredientDetailView = () => import('../views/ingredients/IngredientDetailView.vue')
const IngredientFormView = () => import('../views/ingredients/IngredientFormView.vue')

const CuisineListView = () => import('../views/cuisines/CuisineListView.vue')
const CuisineDetailView = () => import('../views/cuisines/CuisineDetailView.vue')
const CuisineFormView = () => import('../views/cuisines/CuisineFormView.vue')

const FavoriteListView = () => import('../views/favorites/FavoriteListView.vue')
const FavoriteDetailView = () => import('../views/favorites/FavoriteDetailView.vue')
const FavoriteFormView = () => import('../views/favorites/FavoriteFormView.vue')

const routes = [
  { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
  { path: '/register', name: 'register', component: RegisterView, meta: { public: true } },
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'dashboard', component: DashboardView },
      { path: 'recipes', name: 'recipes', component: RecipeListView },
      { path: 'recipes/create', name: 'recipes-create', component: RecipeFormView },
      { path: 'recipes/:id/edit', name: 'recipes-edit', component: RecipeFormView },
      { path: 'recipes/:id', name: 'recipes-detail', component: RecipeDetailView, props: true },
      { path: 'ingredients', name: 'ingredients', component: IngredientListView },
      { path: 'ingredients/create', name: 'ingredients-create', component: IngredientFormView },
      { path: 'ingredients/:id/edit', name: 'ingredients-edit', component: IngredientFormView },
      { path: 'ingredients/:id', name: 'ingredients-detail', component: IngredientDetailView, props: true },
      { path: 'cuisines', name: 'cuisines', component: CuisineListView },
      { path: 'cuisines/create', name: 'cuisines-create', component: CuisineFormView },
      { path: 'cuisines/:id/edit', name: 'cuisines-edit', component: CuisineFormView },
      { path: 'cuisines/:id', name: 'cuisines-detail', component: CuisineDetailView, props: true },
      { path: 'favorites', name: 'favorites', component: FavoriteListView },
      { path: 'favorites/create', name: 'favorites-create', component: FavoriteFormView },
      { path: 'favorites/:id/edit', name: 'favorites-edit', component: FavoriteFormView },
      { path: 'favorites/:id', name: 'favorites-detail', component: FavoriteDetailView, props: true }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const isPublic = Boolean(to.meta.public)

  if (!isPublic && !token) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  if (isPublic && token) {
    next({ name: 'dashboard' })
    return
  }

  next()
})

export default router
