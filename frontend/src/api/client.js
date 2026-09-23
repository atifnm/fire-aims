import axios from 'axios'

// In local dev, the frontend and backend are reached through the same origin (Vite's dev
// server proxies /api and /static to the backend — see vite.config.js), so relative paths
// work with no configuration. On a host like Railway, the frontend and backend are separate
// services with separate public URLs, so VITE_API_URL must be set at build time to the
// backend's public URL (e.g. https://fire-aims-backend-production.up.railway.app, no
// trailing slash) for API calls and file links (QR codes, barcodes, photos) to resolve
// correctly instead of resolving against the frontend's own origin.
const BACKEND_ORIGIN = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: `${BACKEND_ORIGIN}/api`,
})

// Turns a backend-relative path (e.g. "/static/qr/FE-00001_qr.png") into a URL that resolves
// correctly regardless of whether the frontend and backend share an origin. Use this for any
// <img src>/<a href> pointing at a file the backend served a path for (QR codes, barcodes,
// inspection/maintenance photos) — never render those paths directly.
export function assetUrl(path) {
  if (!path) return path
  if (/^https?:\/\//i.test(path)) return path
  return `${BACKEND_ORIGIN}${path}`
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('fireaims_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('fireaims_token')
      localStorage.removeItem('fireaims_user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default api
