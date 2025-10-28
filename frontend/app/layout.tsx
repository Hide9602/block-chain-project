import '../styles/globals.css';
import { I18nProvider } from '@/components/I18nProvider';

export const metadata = {
  title: 'MetaSleuth NextGen - AI-Powered Blockchain Investigation',
  description: 'Advanced pattern detection, risk assessment, and transaction analysis powered by cutting-edge AI technology',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <I18nProvider>{children}</I18nProvider>
      </body>
    </html>
  )
}
