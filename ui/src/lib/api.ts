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

type ApiRequestOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH"
  body?: unknown
  headers?: HeadersInit
  auth?: boolean
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { method = "GET", body, headers, auth = false } = options
  const response = await fetch(apiPath(path), {
    method,
    headers: {
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...(auth ? authHeaders() : {}),
      ...(headers ?? {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  const payload = (await response.json().catch(() => ({}))) as {
    detail?: string | Array<{ msg?: string }>
  }
  if (!response.ok) {
    const { detail } = payload
    if (typeof detail === "string") {
      throw new Error(detail)
    }
    if (Array.isArray(detail)) {
      const msg = detail
        .map((item) => item.msg ?? "")
        .filter(Boolean)
        .join(", ")
      throw new Error(msg || `Request failed (${response.status})`)
    }
    throw new Error(`Request failed (${response.status})`)
  }

  return payload as T
}
