import { useEffect, useMemo, useState } from "react"

import { Button } from "@/components/ui/button"
import { useDevicesQuery } from "@/lib/query/devices"
import { useIntegrationsQuery } from "@/lib/query/integrations"

const getPayloadString = (payload: Record<string, unknown>, key: string) => {
  const value = payload[key]
  return typeof value === "string" && value.trim() ? value : "—"
}

export function DevicesPage() {
  const devicesQuery = useDevicesQuery()
  const integrationsQuery = useIntegrationsQuery()
  const rows = devicesQuery.data ?? []
  const [toggleState, setToggleState] = useState<Record<number, boolean>>({})
  const [menuOpenForId, setMenuOpenForId] = useState<number | null>(null)
  const [payloadModal, setPayloadModal] = useState<{
    deviceName: string
    payload: Record<string, unknown>
  } | null>(null)

  const integrationsMap = useMemo(() => {
    const map = new Map<number, string>()
    for (const row of integrationsQuery.data ?? []) {
      map.set(row.id, `${row.type} (${row.id})`)
    }
    return map
  }, [integrationsQuery.data])

  useEffect(() => {
    setToggleState((prev) => {
      const next = { ...prev }
      for (const row of rows) {
        if (next[row.id] !== undefined) continue
        const dps = row.payload.dps as { dps?: Record<string, unknown> } | undefined
        next[row.id] = dps?.dps?.["20"] === true
      }
      return next
    })
  }, [rows])

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Devices</h1>
          <p className="text-sm text-muted-foreground">
            Registered devices discovered through your integrations.
          </p>
        </div>
      </div>

      {devicesQuery.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : devicesQuery.isError ? (
        <p className="text-sm text-destructive">
          {devicesQuery.error instanceof Error ? devicesQuery.error.message : "Failed to load devices"}
        </p>
      ) : (
        <div className="overflow-x-auto overflow-y-visible rounded-lg border border-border">
          <table className="w-full min-w-[980px] text-left text-sm">
            <thead className="border-b border-border bg-muted/50">
              <tr>
                <th className="px-3 py-2 font-medium">ID</th>
                <th className="px-3 py-2 font-medium">Name</th>
                <th className="px-3 py-2 font-medium">Integration</th>
                <th className="px-3 py-2 font-medium">IP</th>
                <th className="px-3 py-2 font-medium">Device Key</th>
                <th className="px-3 py-2 font-medium">MAC</th>
                <th className="px-3 py-2 font-medium">Version</th>
                <th className="px-3 py-2 font-medium">Controllable</th>
                <th className="px-3 py-2 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td className="px-3 py-6 text-muted-foreground" colSpan={9}>
                    No devices found.
                  </td>
                </tr>
              ) : (
                rows.map((device) => (
                  <tr key={device.id} className="border-b border-border last:border-0">
                    <td className="px-3 py-2 font-mono text-xs">{device.id}</td>
                    <td className="px-3 py-2">
                      {device.name?.trim() || getPayloadString(device.payload, "name")}
                    </td>
                    <td className="px-3 py-2">
                      {integrationsMap.get(device.integration_id) ?? `Unknown (${device.integration_id})`}
                    </td>
                    <td className="px-3 py-2 font-mono text-xs">
                      {device.last_known_ip || getPayloadString(device.payload, "ip")}
                    </td>
                    <td className="px-3 py-2 font-mono text-xs">
                      {getPayloadString(device.payload, "id")}
                    </td>
                    <td className="px-3 py-2 font-mono text-xs">
                      {getPayloadString(device.payload, "mac")}
                    </td>
                    <td className="px-3 py-2">{getPayloadString(device.payload, "ver")}</td>
                    <td className="px-3 py-2">
                      {device.controllable ? (
                        <span className="rounded border border-emerald-400/50 bg-emerald-400/10 px-2 py-0.5 text-xs text-emerald-700 dark:text-emerald-300">
                          Yes
                        </span>
                      ) : (
                        <span className="rounded border border-border px-2 py-0.5 text-xs text-muted-foreground">
                          No
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      <div className="relative flex items-center gap-2">
                        <Button
                          type="button"
                          size="sm"
                          variant="outline"
                          disabled={!device.controllable}
                          onClick={() =>
                            setToggleState((prev) => ({
                              ...prev,
                              [device.id]: !prev[device.id],
                            }))
                          }
                        >
                          {toggleState[device.id] ? "Turn off" : "Turn on"}
                        </Button>
                        <Button
                          type="button"
                          size="icon-sm"
                          variant="outline"
                          aria-label="Open device actions"
                          onClick={() =>
                            setMenuOpenForId((current) => (current === device.id ? null : device.id))
                          }
                        >
                          ...
                        </Button>
                        {menuOpenForId === device.id ? (
                          <div className="absolute right-0 top-10 z-10 min-w-40 rounded-md border border-border bg-card p-1 shadow-lg">
                            <button
                              type="button"
                              className="w-full rounded px-2 py-1.5 text-left text-sm hover:bg-muted"
                              onClick={() => {
                                setPayloadModal({
                                  deviceName:
                                    device.name?.trim() || getPayloadString(device.payload, "name"),
                                  payload: device.payload,
                                })
                                setMenuOpenForId(null)
                              }}
                            >
                              View payload
                            </button>
                          </div>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {payloadModal ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="device-payload-title"
        >
          <div className="w-full max-w-3xl rounded-lg border border-border bg-card p-5 shadow-lg">
            <div className="flex items-center justify-between gap-3">
              <h2 id="device-payload-title" className="text-lg font-semibold">
                Device Payload: {payloadModal.deviceName}
              </h2>
              <Button type="button" variant="outline" onClick={() => setPayloadModal(null)}>
                Close
              </Button>
            </div>
            <pre className="mt-4 max-h-[60vh] overflow-auto rounded-md border border-border bg-muted/30 p-3 text-xs">
              {JSON.stringify(payloadModal.payload, null, 2)}
            </pre>
          </div>
        </div>
      ) : null}
    </div>
  )
}
