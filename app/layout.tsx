import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  title: 'Role Radar — Job Search Command Center',
  description:
    'A focused workspace for reviewing, comparing, and acting on high-fit remote software engineering roles.',
  openGraph: {
    title: 'Role Radar — Job Search Command Center',
    description: 'Strong remote software-engineering roles, clearly ranked and ready for action.',
    type: 'website',
    images: [{ url: '/og.png', width: 1728, height: 909, alt: 'Role Radar — Strong roles, clearly ranked.' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Role Radar — Job Search Command Center',
    description: 'Strong remote software-engineering roles, clearly ranked and ready for action.',
    images: ['/og.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('role-radar-theme');var d=t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme: dark)').matches);document.documentElement.classList.toggle('dark',d)}catch(e){}})()`,
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
