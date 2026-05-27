import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from '@/app/providers';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: 'StudyRoom — Focus Together. Achieve More.',
  description:
    'A collaborative study platform where students create virtual rooms, track sessions, and chat in real time.',
  keywords: ['study room', 'collaborative learning', 'focus timer', 'study together'],
  openGraph: {
    title: 'StudyRoom',
    description: 'Focus Together. Achieve More.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
