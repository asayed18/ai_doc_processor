import '@/styles/globals.css'
import { Inter, Roboto_Flex } from 'next/font/google'
import { Brain, Sparkles } from 'lucide-react'

const inter = Inter({ subsets: ['latin'] })
const roboto = Roboto_Flex({ 
  subsets: ['latin'],
  weight: ['400', '600', '700', '800'],
  display: 'swap'
})

export const metadata = {
  title: 'AI Document Processor',
  description: 'Checklist app for public tender documents',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div className="flex justify-between items-center py-6">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <Brain className="h-10 w-10 from-slate-700 via-gray-700 to-slate-800" />
                    <Sparkles className="h-4 w-4 from-slate-700 via-gray-700 to-slate-800 absolute -top-1 -right-1" />
                  </div>
                  <h1 className={`text-2xl font-extrabold bg-gradient-to-r from-slate-700 via-gray-700 to-slate-800 bg-clip-text text-transparent tracking-tight ${roboto.className}`}>
                    Docy AI
                  </h1>
                </div>
                <p className="text-sm text-gray-600">
                  Checklist app for tender documents
                </p>
              </div>
            </div>
          </header>
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}