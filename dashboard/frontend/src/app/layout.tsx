import './globals.css'
import { ReactNode } from 'react'

export const metadata = {
  title: 'Autonomous Bot Dashboard',
  description: 'Real-time monitoring and control of autonomous bots',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
