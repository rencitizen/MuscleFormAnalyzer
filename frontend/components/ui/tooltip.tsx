"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface TooltipProps {
  children: React.ReactNode
  open?: boolean
  defaultOpen?: boolean
  onOpenChange?: (open: boolean) => void
}

interface TooltipTriggerProps {
  children: React.ReactNode
  asChild?: boolean
  className?: string
}

interface TooltipContentProps {
  children: React.ReactNode
  className?: string
  side?: "top" | "right" | "bottom" | "left"
  sideOffset?: number
}

const TooltipContext = React.createContext<{
  open: boolean
  onOpenChange: (open: boolean) => void
}>({
  open: false,
  onOpenChange: () => {}
})

const TooltipProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>
}

const Tooltip: React.FC<TooltipProps> = ({
  children,
  open: controlledOpen,
  defaultOpen = false,
  onOpenChange
}) => {
  const [uncontrolledOpen, setUncontrolledOpen] = React.useState(defaultOpen)
  const open = controlledOpen !== undefined ? controlledOpen : uncontrolledOpen
  const setOpen = onOpenChange || setUncontrolledOpen

  return (
    <TooltipContext.Provider value={{ open, onOpenChange: setOpen }}>
      <div className="relative inline-block">
        {children}
      </div>
    </TooltipContext.Provider>
  )
}

const TooltipTrigger = React.forwardRef<
  HTMLDivElement,
  TooltipTriggerProps
>(({ children, asChild, className }, ref) => {
  const { onOpenChange } = React.useContext(TooltipContext)

  const handleMouseEnter = () => onOpenChange(true)
  const handleMouseLeave = () => onOpenChange(false)

  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, {
      ...children.props,
      ref,
      onMouseEnter: handleMouseEnter,
      onMouseLeave: handleMouseLeave,
      onFocus: handleMouseEnter,
      onBlur: handleMouseLeave
    })
  }

  return (
    <div
      ref={ref}
      className={className}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleMouseEnter}
      onBlur={handleMouseLeave}
    >
      {children}
    </div>
  )
})
TooltipTrigger.displayName = "TooltipTrigger"

const TooltipContent: React.FC<TooltipContentProps> = ({
  children,
  className,
  side = "top",
  sideOffset = 4
}) => {
  const { open } = React.useContext(TooltipContext)

  if (!open) return null

  const positionStyles = {
    top: `bottom-full left-1/2 -translate-x-1/2 mb-${sideOffset / 4}`,
    bottom: `top-full left-1/2 -translate-x-1/2 mt-${sideOffset / 4}`,
    left: `right-full top-1/2 -translate-y-1/2 mr-${sideOffset / 4}`,
    right: `left-full top-1/2 -translate-y-1/2 ml-${sideOffset / 4}`
  }

  return (
    <div
      className={cn(
        "absolute z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95",
        positionStyles[side],
        className
      )}
    >
      {children}
    </div>
  )
}

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider }