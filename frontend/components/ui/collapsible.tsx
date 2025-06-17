"use client"

import * as React from "react"

interface CollapsibleProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
  className?: string
}

interface CollapsibleTriggerProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
  asChild?: boolean
}

interface CollapsibleContentProps {
  children: React.ReactNode
  className?: string
}

const CollapsibleContext = React.createContext<{
  open: boolean
  onOpenChange: (open: boolean) => void
}>({
  open: false,
  onOpenChange: () => {}
})

const Collapsible: React.FC<CollapsibleProps> = ({
  open = false,
  onOpenChange = () => {},
  children,
  className = ""
}) => {
  return (
    <CollapsibleContext.Provider value={{ open, onOpenChange }}>
      <div className={className}>
        {children}
      </div>
    </CollapsibleContext.Provider>
  )
}

const CollapsibleTrigger = React.forwardRef<
  HTMLButtonElement,
  CollapsibleTriggerProps
>(({ children, className = "", onClick, asChild, ...props }, ref) => {
  const { open, onOpenChange } = React.useContext(CollapsibleContext)
  
  const handleClick = () => {
    onOpenChange(!open)
    onClick?.()
  }

  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, {
      ...children.props,
      onClick: handleClick,
      ref
    })
  }

  return (
    <button
      ref={ref}
      onClick={handleClick}
      className={className}
      {...props}
    >
      {children}
    </button>
  )
})
CollapsibleTrigger.displayName = "CollapsibleTrigger"

const CollapsibleContent: React.FC<CollapsibleContentProps> = ({
  children,
  className = ""
}) => {
  const { open } = React.useContext(CollapsibleContext)
  
  if (!open) return null
  
  return (
    <div className={`transition-all duration-200 ${className}`}>
      {children}
    </div>
  )
}

export { Collapsible, CollapsibleTrigger, CollapsibleContent }