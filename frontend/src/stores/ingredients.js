import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../services/api'

export const useIngredientsStore = defineStore('ingredients', () => {
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
      const { data } = await api.get('/ingredients/', { params: filters.value })
      items.value = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
      totalPages.value = calcTotalPages(data, filters.value)
      return items.value
    } catch (error) {
      console.error('Failed to fetch ingredients:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    loading.value = true
    try {
      const { data } = await api.get(`/ingredients/${id}/`)
      currentItem.value = data
      return data
    } catch (error) {
      console.error('Failed to fetch ingredient:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function create(payload) {
    loading.value = true
    try {
      const { data } = await api.post('/ingredients/', payload)
      return data
    } catch (error) {
      console.error('Failed to create ingredient:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function update(id, payload) {
    loading.value = true
    try {
      const { data } = await api.patch(`/ingredients/${id}/`, payload)
      return data
    } catch (error) {
      console.error('Failed to update ingredient:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function remove(id) {
    loading.value = true
    try {
      await api.delete(`/ingredients/${id}/`)
    } catch (error) {
      console.error('Failed to delete ingredient:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return { items, currentItem, loading, totalPages, filters, fetchAll, fetchOne, create, update, remove }
})
