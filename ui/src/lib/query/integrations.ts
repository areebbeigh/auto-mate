import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { apiRequest } from "@/lib/api"

export type IntegrationRow = {
  id: number
  user_id: number
  type: string
  username: string | null
  access_keys_configured: boolean
  owner_email: string | null
}

export type UpsertIntegrationPayload = {
  targetEditingId: number | null
  body: Record<string, unknown>
}

const integrationsQueryKey = ["integrations"] as const

export function useIntegrationsQuery() {
  return useQuery({
    queryKey: integrationsQueryKey,
    queryFn: () => apiRequest<IntegrationRow[]>("/api/v1/integrations", { auth: true }),
  })
}

export function useIntegrationMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ targetEditingId, body }: UpsertIntegrationPayload) =>
      apiRequest<IntegrationRow>(
        targetEditingId === null
          ? "/api/v1/integrations"
          : `/api/v1/integrations/${targetEditingId}`,
        {
          method: targetEditingId === null ? "POST" : "PUT",
          auth: true,
          body,
        }
      ),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: integrationsQueryKey })
    },
  })
}

export function useDeleteIntegrationMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) =>
      apiRequest<unknown>(`/api/v1/integrations/${id}`, {
        method: "DELETE",
        auth: true,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: integrationsQueryKey })
    },
  })
}
