import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ascendancy",
  description: "Minimal grouped network explorer",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-black text-white">
        {children}
      </body>
    </html>
  );
}
