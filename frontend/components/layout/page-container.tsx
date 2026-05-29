import * as React from "react"
import { cn } from "@/lib/utils"

interface PageContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  size?: "sm" | "md" | "lg" | "xl" | "full"
}

export function PageContainer({
  children,
  className,
  size = "lg",
  ...props
}: PageContainerProps) {
  return (
    <div
      className={cn(
        "mx-auto w-full px-4 md:px-8",
        {
          "max-w-4xl": size === "sm",
          "max-w-5xl": size === "md",
          "max-w-6xl": size === "lg",
          "max-w-7xl": size === "xl",
          "max-w-full": size === "full",
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
