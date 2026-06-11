import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AIAIFrontend UI",
  description: "AI short-film creative console. Currently under active development."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
