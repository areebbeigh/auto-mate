import { Navigate, useOutletContext } from "react-router-dom"

import type { DashboardSession } from "@/dashboard/DashboardLayout"
import { PlaceholderPage } from "@/dashboard/PlaceholderPage"

export function UsersPage() {
  const { session } = useOutletContext<{ session: DashboardSession }>()
  if (!session.is_admin) {
    return <Navigate to="/dashboard/integrations" replace />
  }
  return <PlaceholderPage title="Users" />
}
