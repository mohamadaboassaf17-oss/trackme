import axios from 'axios'

const getBaseURL = () => {
  const envURL = import.meta.env.VITE_API_URL

  if (envURL && envURL.startsWith('http') && !envURL.includes('VITE_API_URL')) {
    return envURL
  }

  if (import.meta.env.PROD) {
    return 'https://trackme-backend-xena.onrender.com/api'
  }

  return 'http://localhost:8000/api'
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => response,
  error => {
    const contentType = error.response?.headers?.['content-type'] || ''
    if (contentType.includes('text/html')) {
      console.error('API Error: Received HTML instead of JSON. Check baseURL:', api.defaults.baseURL)
    }
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      import('@/router').then(({ default: router }) => {
        router.push('/login')
      })
    }
    return Promise.reject(error)
  }
)

console.log('API baseURL:', api.defaults.baseURL)

export default api
