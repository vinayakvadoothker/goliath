import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import { dark } from '@clerk/themes'
import { MainLayout } from '@/components/layout/MainLayout'
import './globals.css'

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
    <ClerkProvider
      appearance={{
        baseTheme: dark,
        variables: {
          colorPrimary: '#6366f1',
          colorBackground: '#0a0a0a',
          colorInputBackground: '#1a1a1a',
          colorInputText: '#f5f5f5',
        },
      }}
    >
      <html lang="en">
        <body className={`${inter.variable} bg-[#0a0a0a] text-[#f5f5f5] font-sans`}>
          <MainLayout>
            {children}
          </MainLayout>
        </body>
      </html>
    </ClerkProvider>
  )
}
