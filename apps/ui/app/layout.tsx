import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { MainLayout } from '@/components/layout/MainLayout'
import { QueryProvider } from '@/components/providers/QueryProvider'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' })

export const metadata: Metadata = {
  title: 'Goliath - Work Assignment',
  description: 'Goliath intelligent work assignment system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} bg-[#0a0a0a] text-[#f5f5f5] font-sans`}>
        <QueryProvider>
          <MainLayout>
            {children}
          </MainLayout>
        </QueryProvider>
      </body>
    </html>
  )
}
