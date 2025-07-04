import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from '../components/ui/toaster'
import { AuthProvider } from '../components/providers/AuthProvider'
import { ThemeProvider } from '../components/providers/ThemeProvider'
import dynamic from 'next/dynamic'
import { LanguageProvider } from '../contexts/LanguageContext'
import { Providers } from './providers'

// 動的インポートでバンドルサイズを削減
const UnifiedNavigation = dynamic(
  () => import('../components/layout/UnifiedNavigation').then(mod => mod.UnifiedNavigation),
  { ssr: true }
)

const FeedbackWidget = dynamic(
  () => import('../components/feedback/FeedbackWidget').then(mod => mod.FeedbackWidget),
  { ssr: false }
)

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TENAX FIT - AI-Powered Fitness Analysis',
  description: 'AI-Powered Fitness Analysis Platform - Analyze your workout form, track body measurements, and optimize your fitness journey',
  manifest: '/manifest.json',
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' }
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' }
    ]
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'TENAX FIT'
  }
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: '#000000',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja" suppressHydrationWarning>
      <head>
        {/* PWA必須メタタグ */}
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="TENAX FIT" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="msapplication-TileColor" content="#000000" />
        <meta name="msapplication-tap-highlight" content="no" />
        
        {/* PWAアイコン設定 */}
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="apple-touch-icon" sizes="152x152" href="/icon-152x152.png" />
        <link rel="apple-touch-icon" sizes="180x180" href="/icon-180x180.png" />
        <link rel="apple-touch-icon" sizes="167x167" href="/icon-167x167.png" />
        
        {/* スプラッシュスクリーン設定 */}
        <link rel="apple-touch-startup-image" href="/splash-640x1136.png" media="(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)" />
        <link rel="apple-touch-startup-image" href="/splash-750x1334.png" media="(device-width: 375px) and (device-height: 667px) and (-webkit-device-pixel-ratio: 2)" />
        <link rel="apple-touch-startup-image" href="/splash-1242x2208.png" media="(device-width: 414px) and (device-height: 736px) and (-webkit-device-pixel-ratio: 3)" />
        <link rel="apple-touch-startup-image" href="/splash-1125x2436.png" media="(device-width: 375px) and (device-height: 812px) and (-webkit-device-pixel-ratio: 3)" />
        
        {/* Favicon設定 */}
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="shortcut icon" href="/favicon.ico" />
      </head>
      <body className={inter.className}>
        <Providers>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <AuthProvider>
              <LanguageProvider>
                <UnifiedNavigation />
                <main className="min-h-[calc(100vh-4rem)] md:min-h-[calc(100vh-4rem)] pb-16 md:pb-0">
                  {children}
                </main>
                {/* <FeedbackWidget /> */}
                <Toaster />
              </LanguageProvider>
            </AuthProvider>
          </ThemeProvider>
        </Providers>
      </body>
    </html>
  )
}