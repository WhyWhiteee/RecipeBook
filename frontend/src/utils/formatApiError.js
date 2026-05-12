/** Из тела ответа DRF в строку для toast */
export function formatApiError(error) {
  if (!error.response) {
    return error.message || 'Ошибка сети'
  }
  const status = error.response.status
  const data = error.response.data
  if (status === 401) return 'Требуется авторизация'
  if (typeof data === 'string') return data
  if (!data || typeof data !== 'object') return `Ошибка ${status}`
  if (data.detail !== undefined) {
    const d = data.detail
    if (Array.isArray(d)) return d.map((x) => (typeof x === 'string' ? x : x.msg || JSON.stringify(x))).join('; ')
    return String(d)
  }
  if (data.non_field_errors) {
    const n = data.non_field_errors
    return Array.isArray(n) ? n.join('; ') : String(n)
  }
  const parts = Object.entries(data).map(([k, v]) => {
    const val = Array.isArray(v) ? v.join(', ') : typeof v === 'object' ? JSON.stringify(v) : String(v)
    return `${k}: ${val}`
  })
  return parts.length ? parts.join('; ') : `Ошибка ${status}`
}
