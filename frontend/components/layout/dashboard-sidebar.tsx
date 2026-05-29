"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BookOpen, LayoutDashboard, DoorOpen, User, LogOut } from "lucide-react"
import { useAuthStore } from "@/store/authStore"
import { useAuth } from "@/hooks/useAuth"
import { ROUTES } from "@/constants"
import { cn } from "@/lib/utils"

const navItems = [
  { href: ROUTES.DASHBOARD, icon: LayoutDashboard, label: "Dashboard" },
  { href: ROUTES.ROOMS, icon: DoorOpen, label: "Study Rooms" },
  { href: ROUTES.PROFILE, icon: User, label: "Profile" },
]

export function DashboardSidebar() {
  const pathname = usePathname()
  const { user } = useAuthStore()
  const { logout } = useAuth()

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-border bg-card">
      <div className="flex h-16 items-center border-b border-border px-6">
        <Link href={ROUTES.HOME} className="flex items-center gap-2 transition-colors hover:text-foreground">
          <BookOpen className="h-5 w-5" />
          <span className="font-semibold tracking-tight">StudyRoom</span>
        </Link>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {navItems.map(({ href, icon: Icon, label }) => {
          const isActive = pathname?.startsWith(href)
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          )
        })}
      </nav>

      <div className="border-t border-border p-4">
        <div className="mb-4 flex items-center gap-3 rounded-md border border-border/50 bg-accent/30 p-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
            {user?.display_name?.[0]?.toUpperCase() ?? "U"}
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="truncate text-sm font-medium leading-none">
              {user?.display_name}
            </p>
            <p className="mt-1 truncate text-xs text-muted-foreground">
              @{user?.username}
            </p>
          </div>
        </div>
        <button
          onClick={() => logout()}
          className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </aside>
  )
}
