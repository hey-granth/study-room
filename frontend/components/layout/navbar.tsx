"use client"

import Link from "next/link"
import { BookOpen } from "lucide-react"
import { useAuthStore } from "@/store/authStore"
import { ROUTES } from "@/constants"
import { Button } from "@/components/ui/button"

export function Navbar() {
  const { isAuthenticated, isHydrated } = useAuthStore()

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-14 max-w-7xl items-center px-4 md:px-8">
        <div className="mr-4 flex">
          <Link href={ROUTES.HOME} className="mr-6 flex items-center space-x-2">
            <BookOpen className="h-5 w-5" />
            <span className="font-semibold tracking-tight">StudyRoom</span>
          </Link>
          <nav className="flex items-center space-x-6 text-sm font-medium">
            <Link
              href={ROUTES.ROOMS}
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Rooms
            </Link>
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-2">
          {isHydrated && isAuthenticated ? (
            <Button asChild variant="default" size="sm">
              <Link href={ROUTES.DASHBOARD}>Dashboard</Link>
            </Button>
          ) : (
            <>
              <Button asChild variant="ghost" size="sm">
                <Link href={ROUTES.LOGIN}>Log in</Link>
              </Button>
              <Button asChild variant="default" size="sm">
                <Link href={ROUTES.REGISTER}>Sign up</Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
