import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "Traffic ML | Prediction & Analytics",
  description:
    "Machine Learning Traffic Prediction and Congestion Analytics System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 antialiased">
        <Sidebar />

        <main className="lg:ml-64">
          {children}
        </main>
      </body>
    </html>
  );
}