import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Goliath - Intelligent Incident Routing',
  description: 'Decision-grade incident routing with evidence-backed assignment',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-[#0a0a0a] text-[#f5f5f5]">{children}</body>
    </html>
  )
}

