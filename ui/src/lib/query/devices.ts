import { useQuery } from "@tanstack/react-query"

import { apiRequest } from "@/lib/api"

export type DeviceRow = {
  id: number
  integration_id: number
  user_id: number
  name: string
  last_known_ip: string | null
  payload: Record<string, unknown>
  controllable: boolean
}

const devicesQueryKey = ["devices"] as const

export function useDevicesQuery() {
  return useQuery({
    queryKey: devicesQueryKey,
    queryFn: () => apiRequest<DeviceRow[]>("/api/v1/devices", { auth: true }),
  })
}
