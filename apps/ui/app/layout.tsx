import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { MainLayout } from '@/components/layout/MainLayout'

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' })

export const metadata: Metadata = {
  title: 'Centra - Work Assignment',
  description: 'Centra intelligent work assignment system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} bg-[#0a0a0a] text-[#f5f5f5] font-sans`}>
        <MainLayout>
          {children}
        </MainLayout>
      </body>
    </html>
  )
}
