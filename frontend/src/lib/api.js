const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

async function fetchJson(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: 'Erro inesperado' }))
    throw new Error(payload.detail || 'Erro de rede')
  }

  return response.json()
}

export const api = {
  getProducts: (params = {}) => {
    const query = new URLSearchParams()

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        query.set(key, String(value))
      }
    })

    const suffix = query.toString() ? `?${query.toString()}` : ''
    return fetchJson(`/products${suffix}`)
  },
  getProductBySlug: (slug) => fetchJson(`/products/${slug}`),
  getCategories: () => fetchJson('/categories'),
  getBrands: () => fetchJson('/brands'),
  getShippingQuote: (payload) =>
    fetchJson('/shipping/quote', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  validateCheckout: (payload) =>
    fetchJson('/checkout/validate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getAdminOverview: (token) =>
    fetchJson('/admin/overview', {
      headers: {
        'X-Admin-Token': token,
      },
    }),
}
