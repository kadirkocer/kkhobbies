import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'
import I18nProvider from './providers/I18nProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Hobi Defteri',
  description: 'Yerel, tek kullanıcı hobi günlüğü',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="tr">
      <body className={inter.className}>
        <Providers>
          <I18nProvider>{children}</I18nProvider>
        </Providers>
      </body>
    </html>
  )
}
