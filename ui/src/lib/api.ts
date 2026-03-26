const ACCESS_TOKEN_KEY = "auto_mate_access_token"

export function getApiBaseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
}

export function getStoredAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function apiPath(path: string): string {
  const base = getApiBaseUrl().replace(/\/$/, "")
  const p = path.startsWith("/") ? path : `/${path}`
  return `${base}${p}`
}

export function authHeaders(): HeadersInit {
  const token = getStoredAccessToken()
  if (!token) return {}
  return { Authorization: `Bearer ${token}` }
}
