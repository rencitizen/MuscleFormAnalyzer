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
  X
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'

const navItems = [
  { href: '/', label: 'ホーム', icon: Home },
  { href: '/analyze', label: 'フォーム分析', icon: Camera },
  { href: '/nutrition', label: '栄養管理', icon: Utensils },
  { href: '/progress', label: '進捗', icon: TrendingUp },
  { href: '/dashboard', label: 'ダッシュボード', icon: BarChart3 },
]

export function MobileNav() {
  const [open, setOpen] = useState(false)
  const pathname = usePathname()

  return (
    <>
      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-background border-t z-50">
        <div className="grid grid-cols-5 h-16">
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
              <SheetTitle>メニュー</SheetTitle>
            </SheetHeader>
            <nav className="mt-6 space-y-4">
              {navItems.map(({ href, label, icon: Icon }) => (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setOpen(false)}
                  className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-secondary"
                >
                  <Icon className="h-5 w-5" />
                  <span>{label}</span>
                </Link>
              ))}
              <hr className="my-4" />
              <Link
                href="/settings"
                onClick={() => setOpen(false)}
                className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-secondary"
              >
                設定
              </Link>
              <Link
                href="/exercises"
                onClick={() => setOpen(false)}
                className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-secondary"
              >
                エクササイズDB
              </Link>
              <Link
                href="/training_data_management"
                onClick={() => setOpen(false)}
                className="flex items-center gap-3 py-2 px-3 rounded-lg hover:bg-secondary"
              >
                データ管理
              </Link>
            </nav>
          </SheetContent>
        </Sheet>
      </div>
    </>
  )
}