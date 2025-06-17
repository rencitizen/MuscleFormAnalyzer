'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  Home,
  Camera,
  Utensils,
  TrendingUp,
  BarChart3,
  Menu,
  X,
  Settings,
  Dumbbell,
  Database
} from 'lucide-react'
import { Button } from '../ui/button'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { useLanguage } from '@/contexts/LanguageContext'

export function MobileNav() {
  const [open, setOpen] = useState(false)
  const pathname = usePathname()
  const { t } = useLanguage()

  const navItems = [
    { href: '/', label: t('navigation.dashboard'), icon: Home },
    { href: '/analyze', label: t('navigation.analyze'), icon: Camera },
    { href: '/nutrition', label: t('navigation.nutrition'), icon: Utensils },
    { href: '/progress', label: t('navigation.progress'), icon: TrendingUp },
  ]

  return (
    <>
      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-background border-t z-50">
        <div className="grid grid-cols-4 h-16">
          {navItems.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href
            return (
              <Link
                key={href}
                href={href}
                className={`flex flex-col items-center justify-center gap-1 text-xs ${
                  isActive ? 'text-primary' : 'text-muted-foreground'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="text-[10px]">{label}</span>
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Mobile Menu Button */}
      <div className="md:hidden fixed top-4 right-4 z-50">
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="outline" size="icon">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent>
            <SheetHeader>
              <SheetTitle>Menu</SheetTitle>
            </SheetHeader>
            <nav className="mt-6 space-y-2">
              <Link
                href="/settings"
                onClick={() => setOpen(false)}
                className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-secondary"
              >
                <Settings className="h-5 w-5" />
                <span>{t('navigation.settings')}</span>
              </Link>
              <Link
                href="/exercises"
                onClick={() => setOpen(false)}
                className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-secondary"
              >
                <Dumbbell className="h-5 w-5" />
                <span>Exercises</span>
              </Link>
            </nav>
          </SheetContent>
        </Sheet>
      </div>
    </>
  )
}