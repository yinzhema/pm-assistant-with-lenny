import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AskProduct',
  description: 'AI-powered product management assistant trained on Lenny\'s Podcast',
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
