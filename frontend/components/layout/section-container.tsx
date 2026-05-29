import * as React from "react"
import { cn } from "@/lib/utils"

export function SectionContainer({
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <section className={cn("py-12 md:py-16 lg:py-24", className)} {...props}>
      {children}
    </section>
  )
}
