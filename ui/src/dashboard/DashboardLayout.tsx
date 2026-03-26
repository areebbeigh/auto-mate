import { useEffect, useState } from "react"
import { NavLink, Outlet, useLocation } from "react-router-dom"
import type { LucideIcon } from "lucide-react"
import {
  CalendarClock,
  Menu,
  MonitorSmartphone,
  Plug,
  ScrollText,
  Settings,
  Users,
  Wrench,
  X,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export type DashboardSession = {
  email: string
  is_admin: boolean
}

type DashboardLayoutProps = {
  session: DashboardSession
  onLogout: () => void
}

const navItems: {
  path: string
  label: string
  adminOnly?: boolean
  Icon: LucideIcon
}[] = [
  { path: "integrations", label: "Integrations", Icon: Plug },
  { path: "devices", label: "Devices", Icon: MonitorSmartphone },
  { path: "users", label: "Users", adminOnly: true, Icon: Users },
  { path: "schedules", label: "Schedules", Icon: CalendarClock },
  { path: "logs", label: "Logs", Icon: ScrollText },
  { path: "settings", label: "Platform Settings", Icon: Settings },
]

export function DashboardLayout({ session, onLogout }: DashboardLayoutProps) {
  const location = useLocation()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const visible = navItems.filter((item) => !item.adminOnly || session.is_admin)

  useEffect(() => {
    setMobileNavOpen(false)
  }, [location.pathname])

  return (
    <div className="flex min-h-screen w-full bg-background text-foreground">
      {mobileNavOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-30 cursor-pointer bg-black/50 md:hidden"
          aria-label="Close menu"
          onClick={() => setMobileNavOpen(false)}
        />
      ) : null}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex w-56 shrink-0 flex-col border-r border-border bg-card shadow-lg transition-transform duration-200 ease-out md:static md:z-auto md:shadow-none",
          mobileNavOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
        )}
      >
        <div className="flex items-center justify-between gap-2 border-b border-border px-4 py-4">
          <div className="flex min-w-0 items-center gap-2">
            <Wrench className="size-6 shrink-0 text-muted-foreground" aria-hidden />
            <span className="truncate text-lg font-semibold tracking-tight">auto-mate</span>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="shrink-0 md:hidden"
            aria-label="Close sidebar"
            onClick={() => setMobileNavOpen(false)}
          >
            <X className="size-4" aria-hidden />
          </Button>
        </div>
        <nav className="flex flex-col gap-0.5 overflow-y-auto p-2">
          {visible.map((item) => {
            const Icon = item.Icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    "flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors",
                    isActive
                      ? "bg-muted font-medium text-foreground"
                      : "text-muted-foreground hover:bg-muted/60 hover:text-foreground",
                  )
                }
              >
                <Icon className="size-4 shrink-0 opacity-80" aria-hidden />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col md:min-h-screen">
        <header className="sticky top-0 z-20 flex items-center justify-between gap-3 border-b border-border bg-background px-4 py-3 md:px-6">
          <div className="flex min-w-0 items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="icon-sm"
              className="shrink-0 md:hidden"
              aria-label="Open menu"
              onClick={() => setMobileNavOpen(true)}
            >
              <Menu className="size-4" aria-hidden />
            </Button>
            <div className="flex min-w-0 items-center gap-2 md:hidden">
              <Wrench className="size-5 shrink-0 text-muted-foreground" aria-hidden />
              <span className="truncate font-semibold tracking-tight">auto-mate</span>
            </div>
          </div>
          <div className="flex min-w-0 items-center gap-2 sm:gap-3">
            <p className="hidden min-w-0 truncate text-sm text-muted-foreground sm:block">
              <span className="text-foreground">{session.email}</span>
              {session.is_admin ? (
                <span className="ml-2 rounded border border-border px-1.5 py-0.5 text-xs">
                  admin
                </span>
              ) : null}
            </p>
            <Button variant="outline" size="sm" onClick={onLogout}>
              Logout
            </Button>
          </div>
        </header>
        <p className="truncate border-b border-border px-4 py-2 text-xs text-muted-foreground sm:hidden">
          <span className="text-foreground">{session.email}</span>
          {session.is_admin ? (
            <span className="ml-2 rounded border border-border px-1.5 py-0.5 text-[10px]">
              admin
            </span>
          ) : null}
        </p>
        <main className="flex-1 overflow-auto p-4 md:p-6">
          <Outlet context={{ session }} />
        </main>
      </div>
    </div>
  )
}
