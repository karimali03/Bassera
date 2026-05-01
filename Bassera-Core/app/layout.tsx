import './globals.css'
import { Inter } from 'next/font/google'
import { AppProvider } from '@/components/providers/AppProvider'
import { Sidebar } from '@/components/layout/Sidebar'
import { TopBar } from '@/components/layout/TopBar'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Baseera - Financial Advisor',
  description: 'Personal finance dashboard powered by AI insights',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AppProvider>
          <Sidebar />
          <TopBar />
          <main className="lg:ml-60 mt-20 p-8">
            {children}
          </main>
        </AppProvider>
      </body>
    </html>
  )
}

