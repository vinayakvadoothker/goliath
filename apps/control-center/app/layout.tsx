import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Goliath Control Center',
  description: 'Interactive incident simulation and routing demo',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
