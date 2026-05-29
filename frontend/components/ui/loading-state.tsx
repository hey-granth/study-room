import * as React from "react"
import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"

interface LoadingStateProps extends React.HTMLAttributes<HTMLDivElement> {
  text?: string
}

export function LoadingState({ text = "Loading...", className, ...props }: LoadingStateProps) {
  return (
    <div
      className={cn("flex min-h-[300px] flex-col items-center justify-center space-y-4", className)}
      {...props}
    >
      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      {text && <p className="text-sm text-muted-foreground">{text}</p>}
    </div>
  )
}
