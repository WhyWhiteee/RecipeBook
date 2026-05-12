import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../services/api'

export const useFavoritesStore = defineStore('favorites', () => {
  const items = ref([])
  const currentItem = ref(null)
  const loading = ref(false)
  const totalPages = ref(0)
  const filters = ref({})

  const calcTotalPages = (data, params = {}) => {
    const pageSize = Number(params.page_size || 20)
    if (typeof data?.count === 'number') return Math.max(1, Math.ceil(data.count / pageSize))
    if (Array.isArray(data?.results) || Array.isArray(data)) return 1
    return 0
  }

  async function fetchAll(params = {}) {
    loading.value = true
    try {
      filters.value = { ...filters.value, ...params }
      const { data } = await api.get('/favorites/', { params: filters.value })
      items.value = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
      totalPages.value = calcTotalPages(data, filters.value)
      return items.value
    } catch (error) {
      console.error('Failed to fetch favorites:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    loading.value = true
    try {
      const { data } = await api.get(`/favorites/${id}/`)
      currentItem.value = data
      return data
    } catch (error) {
      console.error('Failed to fetch favorite:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function create(payload) {
    loading.value = true
    try {
      const { data } = await api.post('/favorites/', payload)
      return data
    } catch (error) {
      console.error('Failed to create favorite:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function update(id, payload) {
    loading.value = true
    try {
      const { data } = await api.patch(`/favorites/${id}/`, payload)
      return data
    } catch (error) {
      console.error('Failed to update favorite:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function remove(id) {
    loading.value = true
    try {
      await api.delete(`/favorites/${id}/`)
    } catch (error) {
      console.error('Failed to delete favorite:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return { items, currentItem, loading, totalPages, filters, fetchAll, fetchOne, create, update, remove }
})
