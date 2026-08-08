import * as React from "react"
import { Progress as ProgressPrimitive } from "radix-ui"

import { cn } from "@/lib/utils"

function Progress({
  className,
  value,
  ...props
}: React.ComponentProps<typeof ProgressPrimitive.Root>) {
  const safeValue = Math.min(100, Math.max(0, value ?? 0))

  return (
    <ProgressPrimitive.Root
      data-slot="progress"
      value={safeValue}
      className={cn(
        "relative flex h-1 w-full items-center overflow-x-hidden rounded-full bg-muted",
        className
      )}
      {...props}
    >
      <ProgressPrimitive.Indicator
        data-slot="progress-indicator"
        className="size-full flex-1 bg-primary transition-all motion-reduce:transition-none"
        style={{ transform: `translateX(-${100 - safeValue}%)` }}
      />
    </ProgressPrimitive.Root>
  )
}

export { Progress }
