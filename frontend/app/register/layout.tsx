import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Sign Up — StudyRoom",
  description: "Create your StudyRoom account.",
}

export default function RegisterLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background bg-grid py-12">
      <div className="absolute inset-0 bg-background/90" />
      <div className="relative w-full max-w-md px-6 z-10">{children}</div>
    </div>
  )
}
