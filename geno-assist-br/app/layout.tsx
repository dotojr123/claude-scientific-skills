import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'GenoAssist BR',
  description: 'Assistente de Genética Clínica',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
