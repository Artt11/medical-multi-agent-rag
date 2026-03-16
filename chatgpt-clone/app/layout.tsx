import "./globals.css";
import { IBM_Plex_Sans, Sora } from "next/font/google";

const sora = Sora({
  subsets: ["latin"],
  variable: "--font-sora",
  display: "swap"
});

const plex = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-plex",
  display: "swap"
});

export const metadata = {
  title: "Nimbus Chat",
  description: "A ChatGPT-style interface with real LLM streaming."
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${sora.variable} ${plex.variable}`}>
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}
