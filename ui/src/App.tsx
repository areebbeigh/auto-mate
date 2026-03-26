import { type FormEvent, useEffect, useMemo, useState } from "react"
import { Navigate, Route, Routes, useNavigate } from "react-router-dom"

import { Button, buttonVariants } from "@/components/ui/button"
import { DashboardLayout } from "@/dashboard/DashboardLayout"
import { IntegrationsPage } from "@/dashboard/IntegrationsPage"
import { PlaceholderPage } from "@/dashboard/PlaceholderPage"
import { UsersPage } from "@/dashboard/UsersPage"

type BootstrapResponse = { is_setup: boolean }
type AuthResponse = {
  user_id: number
  email: string
  is_admin: boolean
  message: string
  access_token: string
  token_type: string
}
type BootstrapMode = "loading" | "setup" | "login"
type Session = { token: string; user: AuthResponse }

const ACCESS_TOKEN_KEY = "auto_mate_access_token"

function App() {
  const [bootstrapMode, setBootstrapMode] = useState<BootstrapMode>("loading")
  const [session, setSession] = useState<Session | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [setupEmail, setSetupEmail] = useState("")
  const [setupPassword, setSetupPassword] = useState("")
  const [setupConfirmPassword, setSetupConfirmPassword] = useState("")
  const [loginEmail, setLoginEmail] = useState("")
  const [loginPassword, setLoginPassword] = useState("")
  const navigate = useNavigate()

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"

  const authHeaders = useMemo(
    () =>
      session
        ? ({
            Authorization: `Bearer ${session.token}`,
          } satisfies HeadersInit)
        : undefined,
    [session]
  )

  const fetchBootstrap = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/bootstrap`)
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }
      const data = (await response.json()) as BootstrapResponse
      setBootstrapMode(data.is_setup ? "login" : "setup")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error")
    }
  }

  const persistSession = (auth: AuthResponse) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, auth.access_token)
    setSession({ token: auth.access_token, user: auth })
  }

  const clearSession = () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    setSession(null)
  }

  const restoreSession = async (token: string) => {
    const response = await fetch(`${apiBaseUrl}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!response.ok) {
      throw new Error("Session expired. Please login again.")
    }
    const auth = (await response.json()) as AuthResponse
    persistSession(auth)
    navigate("/dashboard", { replace: true })
  }

  const submitSetup = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (setupPassword !== setupConfirmPassword) {
      setError("Passwords do not match.")
      return
    }
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/auth/setup-first-user`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: setupEmail, password: setupPassword }),
      })
      const payload = await response.json()
      if (!response.ok) {
        throw new Error(payload.detail ?? `Request failed with status ${response.status}`)
      }
      const data = payload as AuthResponse
      persistSession(data)
      navigate("/dashboard", { replace: true })
      setSetupPassword("")
      setSetupConfirmPassword("")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error")
    } finally {
      setLoading(false)
    }
  }

  const submitLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: loginEmail, password: loginPassword }),
      })
      const payload = await response.json()
      if (!response.ok) {
        throw new Error(payload.detail ?? `Request failed with status ${response.status}`)
      }
      const data = payload as AuthResponse
      persistSession(data)
      setLoginPassword("")
      navigate("/dashboard", { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const run = async () => {
      setLoading(true)
      setError(null)
      try {
        await fetchBootstrap()
        const token = localStorage.getItem(ACCESS_TOKEN_KEY)
        if (token) {
          await restoreSession(token)
        }
      } catch (err) {
        clearSession()
        setError(err instanceof Error ? err.message : "Unexpected error")
      } finally {
        setLoading(false)
      }
    }
    void run()
  }, [])

  const renderAuthScreen = () => (
    <div className="w-full max-w-xl rounded-lg border bg-card p-4 text-left text-sm space-y-3">
      {bootstrapMode === "loading" && <p>Checking app bootstrap...</p>}

      {bootstrapMode === "setup" && (
        <form className="space-y-3" onSubmit={submitSetup}>
          <h2 className="text-lg font-medium">First User Setup</h2>
          <input
            className="w-full rounded-md border bg-background px-3 py-2"
            placeholder="Email"
            type="email"
            value={setupEmail}
            onChange={(event) => setSetupEmail(event.target.value)}
            required
          />
          <input
            className="w-full rounded-md border bg-background px-3 py-2"
            placeholder="Password (min 8 chars)"
            type="password"
            value={setupPassword}
            onChange={(event) => setSetupPassword(event.target.value)}
            required
            minLength={8}
          />
          <input
            className="w-full rounded-md border bg-background px-3 py-2"
            placeholder="Confirm Password"
            type="password"
            value={setupConfirmPassword}
            onChange={(event) => setSetupConfirmPassword(event.target.value)}
            required
            minLength={8}
          />
          <Button type="submit" disabled={loading}>
            {loading ? "Creating user..." : "Create first user"}
          </Button>
        </form>
      )}

      {bootstrapMode === "login" && (
        <form className="space-y-3" onSubmit={submitLogin}>
          <h2 className="text-lg font-medium">Login</h2>
          <input
            className="w-full rounded-md border bg-background px-3 py-2"
            placeholder="Email"
            type="email"
            value={loginEmail}
            onChange={(event) => setLoginEmail(event.target.value)}
            required
          />
          <input
            className="w-full rounded-md border bg-background px-3 py-2"
            placeholder="Password"
            type="password"
            value={loginPassword}
            onChange={(event) => setLoginPassword(event.target.value)}
            required
          />
          <Button type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </Button>
        </form>
      )}

      {error && <p className="text-destructive">Error: {error}</p>}
    </div>
  )

  const handleLogout = () => {
    clearSession()
    setBootstrapMode("login")
    navigate("/auth", { replace: true })
  }

  return (
    <Routes>
      <Route
        path="/"
        element={<Navigate to={session ? "/dashboard" : "/auth"} replace />}
      />
      <Route
        path="/auth"
        element={
          session ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <main className="min-h-screen bg-background text-foreground">
              <div className="mx-auto flex min-h-screen max-w-4xl flex-col items-center justify-center gap-6 px-6 text-center">
                <h1 className="text-4xl font-semibold tracking-tight">auto-mate UI</h1>
                <p className="max-w-2xl text-muted-foreground">
                  Bootstrap-driven auth flow with first-user setup and login.
                </p>
                {renderAuthScreen()}
                <div className="flex items-center gap-3">
                  <Button
                    onClick={async () => {
                      setLoading(true)
                      setError(null)
                      try {
                        await fetchBootstrap()
                        if (session) {
                          const response = await fetch(`${apiBaseUrl}/api/v1/auth/me`, {
                            headers: authHeaders,
                          })
                          if (!response.ok) {
                            clearSession()
                          }
                        }
                      } finally {
                        setLoading(false)
                      }
                    }}
                    disabled={loading}
                  >
                    {loading ? "Refreshing..." : "Refresh bootstrap"}
                  </Button>
                  <a
                    className={buttonVariants({ variant: "outline" })}
                    href={`${apiBaseUrl}/docs`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Open FastAPI docs
                  </a>
                </div>
              </div>
            </main>
          )
        }
      />
      <Route
        path="/dashboard"
        element={
          session ? (
            <DashboardLayout
              session={{
                email: session.user.email,
                is_admin: session.user.is_admin,
              }}
              onLogout={handleLogout}
            />
          ) : (
            <Navigate to="/auth" replace />
          )
        }
      >
        <Route index element={<Navigate to="integrations" replace />} />
        <Route path="integrations" element={<IntegrationsPage />} />
        <Route path="devices" element={<PlaceholderPage title="Devices" />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="schedules" element={<PlaceholderPage title="Schedules" />} />
        <Route path="logs" element={<PlaceholderPage title="Logs" />} />
        <Route path="settings" element={<PlaceholderPage title="Platform Settings" />} />
      </Route>
      <Route
        path="*"
        element={<Navigate to={session ? "/dashboard" : "/auth"} replace />}
      />
    </Routes>
  )
}

export default App
