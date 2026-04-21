import { type SubmitEventHandler, useState } from "react"
import { useOutletContext } from "react-router-dom"

import type { DashboardSession } from "@/dashboard/DashboardLayout"
import { Button } from "@/components/ui/button"
import {
  type IntegrationRow,
  useDeleteIntegrationMutation,
  useIntegrationMutation,
  useIntegrationsQuery,
} from "@/lib/query/integrations"

type FormState = {
  type: "TINYTUYA" | "TAPO"
  access_key: string
  access_key_secret: string
  username: string
  password: string
  user_id: string
}

const emptyForm = (): FormState => ({
  type: "TINYTUYA",
  access_key: "",
  access_key_secret: "",
  username: "",
  password: "",
  user_id: "",
})

export function IntegrationsPage() {
  const { session } = useOutletContext<{ session: DashboardSession }>()
  const isAdmin = session.is_admin

  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState<FormState>(emptyForm)
  const integrationsQuery = useIntegrationsQuery()
  const saveMutation = useIntegrationMutation()
  const deleteMutation = useDeleteIntegrationMutation()
  const rows = integrationsQuery.data ?? []

  const openCreate = () => {
    setError(null)
    setEditingId(null)
    setForm(emptyForm())
    setModalOpen(true)
  }

  const openEdit = (row: IntegrationRow) => {
    setError(null)
    setEditingId(row.id)
    setForm({
      type: row.type === "TAPO" ? "TAPO" : "TINYTUYA",
      access_key: "",
      access_key_secret: "",
      username: row.username ?? "",
      password: "",
      user_id: "",
    })
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setEditingId(null)
    setForm(emptyForm())
  }

  const submit: SubmitEventHandler<HTMLFormElement> = async (event) => {
    event.preventDefault()
    setError(null)
    const body: Record<string, unknown> = { type: form.type }
    if (form.type === "TINYTUYA") {
      body.access_key = form.access_key
      body.access_key_secret = form.access_key_secret
    } else {
      body.username = form.username
      body.password = form.password
    }
    if (isAdmin && form.user_id.trim() !== "") {
      body.user_id = Number.parseInt(form.user_id, 10)
    }

    try {
      await saveMutation.mutateAsync({ targetEditingId: editingId, body })
      closeModal()
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed")
    }
  }

  const remove = async (id: number) => {
    if (!window.confirm("Delete this integration? Devices using it will be removed.")) {
      return
    }
    setError(null)
    try {
      await deleteMutation.mutateAsync(id)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed")
    }
  }

  const credentialSummary = (row: IntegrationRow) => {
    if (row.type.toUpperCase() === "TAPO") {
      return row.username ? `User: ${row.username}` : "—"
    }
    return row.access_keys_configured ? "Access keys configured" : "—"
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Integrations</h1>
          <p className="text-sm text-muted-foreground">
            TinyTuya uses access key + secret. Tapo uses username + password.
          </p>
        </div>
        {isAdmin ? (
          <Button type="button" onClick={openCreate}>
            Add integration
          </Button>
        ) : null}
      </div>

      {error && !modalOpen ? (
        <p className="text-sm text-destructive">{error}</p>
      ) : null}

      {integrationsQuery.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : integrationsQuery.isError ? (
        <p className="text-sm text-destructive">
          {integrationsQuery.error instanceof Error
            ? integrationsQuery.error.message
            : "Failed to load"}
        </p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50">
              <tr>
                <th className="px-3 py-2 font-medium">ID</th>
                <th className="px-3 py-2 font-medium">Type</th>
                {session.is_admin ? (
                  <th className="px-3 py-2 font-medium">Owner</th>
                ) : null}
                <th className="px-3 py-2 font-medium">Credentials</th>
                {isAdmin ? <th className="px-3 py-2 font-medium w-[140px]">Actions</th> : null}
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td
                    className="px-3 py-6 text-muted-foreground"
                    colSpan={session.is_admin ? 5 : 3}
                  >
                    No integrations yet.
                  </td>
                </tr>
              ) : (
                rows.map((row) => (
                  <tr key={row.id} className="border-b border-border last:border-0">
                    <td className="px-3 py-2 font-mono text-xs">{row.id}</td>
                    <td className="px-3 py-2">{row.type}</td>
                    {session.is_admin ? (
                      <td className="px-3 py-2">{row.owner_email ?? "—"}</td>
                    ) : null}
                    <td className="px-3 py-2 text-muted-foreground">{credentialSummary(row)}</td>
                    {isAdmin ? (
                      <td className="px-3 py-2">
                        <div className="flex flex-wrap gap-2">
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => openEdit(row)}
                          >
                            Edit
                          </Button>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            className="text-destructive hover:text-destructive"
                            onClick={() => void remove(row.id)}
                          >
                            Delete
                          </Button>
                        </div>
                      </td>
                    ) : null}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {modalOpen ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="integration-modal-title"
        >
          <div className="w-full max-w-md rounded-lg border border-border bg-card p-5 shadow-lg">
            <h2 id="integration-modal-title" className="text-lg font-semibold">
              {editingId === null ? "New integration" : `Edit integration #${editingId}`}
            </h2>
            <p className="mt-1 text-xs text-muted-foreground">
              {editingId !== null
                ? "Re-enter all credentials; stored secrets are not shown."
                : null}
            </p>

            {error ? <p className="mt-2 text-sm text-destructive">{error}</p> : null}

            <form className="mt-4 space-y-3" onSubmit={submit}>
              <label className="block text-sm">
                <span className="text-muted-foreground">Type</span>
                <select
                  className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2"
                  value={form.type}
                  onChange={(e) =>
                    setForm((f) => ({
                      ...f,
                      type: e.target.value as "TINYTUYA" | "TAPO",
                    }))
                  }
                >
                  <option value="TINYTUYA">TinyTuya</option>
                  <option value="TAPO">Tapo</option>
                </select>
              </label>

              {form.type === "TINYTUYA" ? (
                <>
                  <label className="block text-sm">
                    <span className="text-muted-foreground">Access key</span>
                    <input
                      className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 font-mono text-xs"
                      value={form.access_key}
                      onChange={(e) => setForm((f) => ({ ...f, access_key: e.target.value }))}
                      autoComplete="off"
                      required
                    />
                  </label>
                  <label className="block text-sm">
                    <span className="text-muted-foreground">Access key secret</span>
                    <input
                      type="password"
                      className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 font-mono text-xs"
                      value={form.access_key_secret}
                      onChange={(e) =>
                        setForm((f) => ({ ...f, access_key_secret: e.target.value }))
                      }
                      autoComplete="off"
                      required
                    />
                  </label>
                </>
              ) : (
                <>
                  <label className="block text-sm">
                    <span className="text-muted-foreground">Username</span>
                    <input
                      className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2"
                      value={form.username}
                      onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
                      autoComplete="username"
                      required
                    />
                  </label>
                  <label className="block text-sm">
                    <span className="text-muted-foreground">Password</span>
                    <input
                      type="password"
                      className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2"
                      value={form.password}
                      onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                      autoComplete="current-password"
                      required
                    />
                  </label>
                </>
              )}

              {isAdmin && editingId === null ? (
                <label className="block text-sm">
                  <span className="text-muted-foreground">User ID (optional)</span>
                  <input
                    className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2"
                    placeholder="Defaults to you"
                    value={form.user_id}
                    onChange={(e) => setForm((f) => ({ ...f, user_id: e.target.value }))}
                    inputMode="numeric"
                  />
                </label>
              ) : null}

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" onClick={closeModal}>
                  Cancel
                </Button>
                <Button type="submit" disabled={saveMutation.isPending}>
                  {saveMutation.isPending ? "Saving…" : "Save"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  )
}
