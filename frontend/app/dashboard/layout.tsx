"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/authStore"
import { ROUTES } from "@/constants"
import { DashboardSidebar } from "@/components/layout/dashboard-sidebar"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { isAuthenticated, isHydrated } = useAuthStore()

  useEffect(() => {
    if (isHydrated && !isAuthenticated) {
      router.push(ROUTES.LOGIN)
    }
  }, [isAuthenticated, isHydrated, router])

  if (!isHydrated || !isAuthenticated) return null

  return (
    <div className="flex min-h-screen bg-background">
      <DashboardSidebar />
      <main className="flex-1 pl-64">
        <div className="mx-auto max-w-6xl p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
