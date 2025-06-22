'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/components/providers/AuthProvider'
import { useLanguage } from '@/contexts/LanguageContext'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import {
  Home,
  Camera,
  Utensils,
  TrendingUp,
  Dumbbell,
  Brain,
  User,
  Settings,
  LogOut,
  Menu,
  X,
  ChartBar,
  Activity,
  Target,
  Calendar,
  FileText,
  HelpCircle,
  Sparkles,
  Microscope,
  Zap,
  Trophy,
  Heart,
  Users,
  MessageSquare,
  Bell,
  Search,
  Filter,
  Plus
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { motion, AnimatePresence } from 'framer-motion'

interface NavItem {
  href: string
  label: string
  labelEn: string
  icon: React.ElementType
  badge?: string
  description?: string
  descriptionEn?: string
  subItems?: NavItem[]
  isNew?: boolean
  isPro?: boolean
}

const navigationItems: NavItem[] = [
  {
    href: '/',
    label: 'ダッシュボード',
    labelEn: 'Dashboard',
    icon: Home,
    description: 'トレーニングの概要と今日のタスク',
    descriptionEn: 'Training overview and today\'s tasks'
  },
  {
    href: '/analyze',
    label: 'フォーム分析',
    labelEn: 'Form Analysis',
    icon: Camera,
    description: 'AIによるリアルタイムフォーム解析',
    descriptionEn: 'Real-time form analysis with AI',
    isNew: true
  },
  {
    href: '/progress',
    label: '進捗管理',
    labelEn: 'Progress',
    icon: TrendingUp,
    description: 'トレーニング記録と成長の可視化',
    descriptionEn: 'Training records and growth visualization'
  },
  {
    href: '/exercises',
    label: 'エクササイズ',
    labelEn: 'Exercises',
    icon: Dumbbell,
    description: '運動データベースとガイド',
    descriptionEn: 'Exercise database and guides',
    subItems: [
      {
        href: '/exercises',
        label: 'エクササイズ一覧',
        labelEn: 'Exercise List',
        icon: Dumbbell
      },
      {
        href: '/exercises/browser',
        label: 'エクササイズ検索',
        labelEn: 'Exercise Browser',
        icon: Search
      }
    ]
  },
  {
    href: '/training',
    label: 'トレーニング',
    labelEn: 'Training',
    icon: Activity,
    description: 'ワークアウトプランと実行',
    descriptionEn: 'Workout plans and execution'
  },
  {
    href: '/training-generator',
    label: 'AI トレーナー',
    labelEn: 'AI Trainer',
    icon: Brain,
    description: 'パーソナライズされたトレーニング生成',
    descriptionEn: 'Personalized training generation',
    badge: 'AI',
    isPro: true
  },
  {
    href: '/v3',
    label: '科学的分析',
    labelEn: 'Scientific Analysis',
    icon: Microscope,
    description: '体組成・代謝の詳細分析',
    descriptionEn: 'Detailed body composition & metabolism',
    badge: 'V3',
    isNew: true
  },
  {
    href: '/dashboard/scientific',
    label: '科学的指標',
    labelEn: 'Scientific Metrics',
    icon: Sparkles,
    description: '高度なフィットネス指標',
    descriptionEn: 'Advanced fitness metrics'
  }
]

const quickActions = [
  {
    label: '新規トレーニング',
    labelEn: 'New Training',
    icon: Plus,
    href: '/training/new',
    color: 'bg-green-500'
  },
  {
    label: 'フォーム撮影',
    labelEn: 'Capture Form',
    icon: Camera,
    href: '/analyze',
    color: 'bg-purple-500'
  },
  {
    label: '進捗更新',
    labelEn: 'Update Progress',
    icon: TrendingUp,
    href: '/progress/update',
    color: 'bg-orange-500'
  },
  {
    label: 'エクササイズ',
    labelEn: 'Exercises',
    icon: Dumbbell,
    href: '/exercises',
    color: 'bg-blue-500'
  }
]

export function UnifiedNavigation() {
  const pathname = usePathname()
  const { user, logout } = useAuth()
  const { language } = useLanguage()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const t = (label: string, labelEn: string) => language === 'ja' ? label : labelEn

  const filteredNavItems = navigationItems.filter(item => 
    item.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.labelEn.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.descriptionEn?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const NavLink = ({ item, mobile = false }: { item: NavItem; mobile?: boolean }) => {
    const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
    const hasSubItems = item.subItems && item.subItems.length > 0

    if (hasSubItems && !mobile) {
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className={cn(
                'justify-start gap-2 relative',
                isActive && 'bg-accent text-accent-foreground'
              )}
            >
              <item.icon className="h-4 w-4" />
              <span className="hidden lg:inline">{t(item.label, item.labelEn)}</span>
              {item.badge && (
                <Badge variant="secondary" className="ml-auto h-5 text-xs">
                  {item.badge}
                </Badge>
              )}
              {item.isNew && (
                <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-red-500 animate-pulse" />
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-56">
            <DropdownMenuLabel>{t(item.label, item.labelEn)}</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {item.subItems.map((subItem) => (
              <DropdownMenuItem key={subItem.href} asChild>
                <Link href={subItem.href} className="flex items-center gap-2">
                  <subItem.icon className="h-4 w-4" />
                  {t(subItem.label, subItem.labelEn)}
                </Link>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      )
    }

    return (
      <Link
        href={item.href}
        className={cn(
          'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all hover:bg-accent relative group',
          isActive && 'bg-accent text-accent-foreground font-medium',
          mobile && 'py-3'
        )}
        onClick={() => mobile && setIsMobileMenuOpen(false)}
      >
        <item.icon className={cn('h-4 w-4', mobile && 'h-5 w-5')} />
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span>{t(item.label, item.labelEn)}</span>
            {item.badge && (
              <Badge variant="secondary" className="h-5 text-xs">
                {item.badge}
              </Badge>
            )}
            {item.isNew && (
              <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
            )}
          </div>
          {mobile && item.description && (
            <p className="text-xs text-muted-foreground mt-1">
              {t(item.description, item.descriptionEn)}
            </p>
          )}
        </div>
        {item.isPro && (
          <Badge variant="outline" className="ml-auto">
            PRO
          </Badge>
        )}
      </Link>
    )
  }

  return (
    <>
      {/* Desktop Header */}
      <header className="hidden md:flex sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center gap-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 font-bold text-xl">
            <Zap className="h-6 w-6 text-primary" />
            TENAX FIT
          </Link>

          {/* Main Navigation */}
          <nav className="flex-1 flex items-center gap-2 ml-8">
            {navigationItems.slice(0, 6).map((item) => (
              <NavLink key={item.href} item={item} />
            ))}
          </nav>

          {/* Quick Actions */}
          <div className="flex items-center gap-2">
            {/* Search */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSearchOpen(!isSearchOpen)}
            >
              <Search className="h-4 w-4" />
            </Button>

            {/* Notifications */}
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-4 w-4" />
              <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-red-500 flex items-center justify-center text-[8px] text-white font-bold">
                3
              </span>
            </Button>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                  <Avatar className="h-9 w-9">
                    <AvatarImage src={user?.photoURL || ''} alt={user?.displayName || ''} />
                    <AvatarFallback>{user?.displayName?.[0] || 'U'}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user?.displayName}</p>
                    <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/profile" className="flex items-center">
                    <User className="mr-2 h-4 w-4" />
                    {t('プロフィール', 'Profile')}
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/settings" className="flex items-center">
                    <Settings className="mr-2 h-4 w-4" />
                    {t('設定', 'Settings')}
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/help" className="flex items-center">
                    <HelpCircle className="mr-2 h-4 w-4" />
                    {t('ヘルプ', 'Help')}
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => logout()} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  {t('ログアウト', 'Logout')}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Mobile Header */}
      <header className="md:hidden sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-14 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2 font-bold text-lg">
            <Zap className="h-5 w-5 text-primary" />
            TENAX FIT
          </Link>
          
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-red-500 flex items-center justify-center text-[8px] text-white font-bold">
                3
              </span>
            </Button>
            <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-[85%] sm:w-[385px] p-0">
                <SheetHeader className="border-b p-4">
                  <SheetTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Zap className="h-5 w-5 text-primary" />
                      メニュー
                    </span>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      <X className="h-5 w-5" />
                    </Button>
                  </SheetTitle>
                </SheetHeader>
                
                {/* User Info */}
                <div className="p-4 border-b">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={user?.photoURL || ''} alt={user?.displayName || ''} />
                      <AvatarFallback>{user?.displayName?.[0] || 'U'}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <p className="font-medium">{user?.displayName}</p>
                      <p className="text-sm text-muted-foreground">{user?.email}</p>
                    </div>
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="p-4 border-b">
                  <h3 className="text-sm font-medium mb-3">クイックアクション</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {quickActions.map((action) => (
                      <Link
                        key={action.href}
                        href={action.href}
                        onClick={() => setIsMobileMenuOpen(false)}
                        className="flex flex-col items-center gap-2 p-3 rounded-lg border hover:bg-accent transition-colors"
                      >
                        <div className={cn('h-10 w-10 rounded-full flex items-center justify-center', action.color)}>
                          <action.icon className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-xs text-center">{t(action.label, action.labelEn)}</span>
                      </Link>
                    ))}
                  </div>
                </div>

                {/* Navigation */}
                <ScrollArea className="flex-1 px-4">
                  <div className="space-y-1 py-4">
                    {navigationItems.map((item) => (
                      <NavLink key={item.href} item={item} mobile />
                    ))}
                  </div>
                </ScrollArea>

                {/* Bottom Actions */}
                <div className="border-t p-4 space-y-2">
                  <Link
                    href="/settings"
                    className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <Settings className="h-4 w-4" />
                    {t('設定', 'Settings')}
                  </Link>
                  <Link
                    href="/help"
                    className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <HelpCircle className="h-4 w-4" />
                    {t('ヘルプ', 'Help')}
                  </Link>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-red-600"
                    onClick={() => {
                      logout()
                      setIsMobileMenuOpen(false)
                    }}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    {t('ログアウト', 'Logout')}
                  </Button>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </header>

      {/* Search Overlay */}
      <AnimatePresence>
        {isSearchOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-16 left-0 right-0 z-40 bg-background border-b p-4 shadow-lg"
          >
            <div className="container max-w-2xl mx-auto">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder={t('機能を検索...', 'Search features...')}
                  className="pl-10 pr-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  autoFocus
                />
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8"
                  onClick={() => {
                    setIsSearchOpen(false)
                    setSearchQuery('')
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              
              {searchQuery && (
                <div className="mt-4 space-y-2">
                  {filteredNavItems.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      {t('検索結果が見つかりません', 'No results found')}
                    </p>
                  ) : (
                    filteredNavItems.map((item) => (
                      <Link
                        key={item.href}
                        href={item.href}
                        className="flex items-center gap-3 p-3 rounded-lg hover:bg-accent transition-colors"
                        onClick={() => {
                          setIsSearchOpen(false)
                          setSearchQuery('')
                        }}
                      >
                        <item.icon className="h-5 w-5" />
                        <div className="flex-1">
                          <p className="font-medium">{t(item.label, item.labelEn)}</p>
                          {item.description && (
                            <p className="text-sm text-muted-foreground">
                              {t(item.description, item.descriptionEn)}
                            </p>
                          )}
                        </div>
                        {item.badge && (
                          <Badge variant="secondary">{item.badge}</Badge>
                        )}
                      </Link>
                    ))
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Mobile Bottom Navigation - Enhanced */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-background border-t">
        <div className="grid grid-cols-5 h-16">
          {[
            { href: '/', label: 'ホーム', labelEn: 'Home', icon: Home },
            { href: '/analyze', label: '分析', labelEn: 'Analyze', icon: Camera },
            { href: '/training/new', label: '', labelEn: '', icon: Plus, isAction: true },
            { href: '/exercises', label: '種目', labelEn: 'Exercise', icon: Dumbbell },
            { href: '/progress', label: '進捗', labelEn: 'Progress', icon: TrendingUp },
          ].map((item, index) => {
            const isActive = pathname === item.href
            
            if (item.isAction) {
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center justify-center"
                >
                  <div className="h-12 w-12 rounded-full bg-primary flex items-center justify-center shadow-lg">
                    <item.icon className="h-6 w-6 text-primary-foreground" />
                  </div>
                </Link>
              )
            }
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex flex-col items-center justify-center gap-1 text-xs',
                  isActive ? 'text-primary' : 'text-muted-foreground'
                )}
              >
                <item.icon className="h-5 w-5" />
                <span>{t(item.label, item.labelEn)}</span>
              </Link>
            )
          })}
        </div>
      </nav>
    </>
  )
}