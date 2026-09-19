"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Brain,
  BarChart3,
  CloudSun,
  Activity,
  Gauge,
  Radio,
} from "lucide-react";

const navigation = [
  {
    name: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    name: "Live Traffic",
    href: "/live-traffic",
    icon: Radio,
  },
  {
    name: "Prediction",
    href: "/prediction",
    icon: Brain,
  },
  {
    name: "Analytics",
    href: "/analytics",
    icon: BarChart3,
  },
  {
    name: "Forecast",
    href: "/forecast",
    icon: Activity,
  },
  {
    name: "Weather",
    href: "/weather",
    icon: CloudSun,
  },
  {
    name: "Model Performance",
    href: "/model-performance",
    icon: Gauge,
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 hidden h-screen w-64 border-r border-slate-200 bg-white lg:block">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="border-b border-slate-200 px-6 py-6">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
              <Activity size={21} />
            </div>

            <div>
              <p className="font-bold tracking-tight">
                Traffic ML
              </p>

              <p className="text-xs text-slate-400">
                Analytics System
              </p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-5">
          <p className="px-3 pb-3 text-[10px] font-bold uppercase tracking-widest text-slate-400">
            Navigation
          </p>

          {navigation.map((item) => {
            const Icon = item.icon;

            const active =
              pathname === item.href ||
              (item.href !== "/" &&
                pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
                  active
                    ? "bg-slate-900 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                <Icon size={18} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* System status */}
        <div className="border-t border-slate-200 p-5">
          <div className="rounded-xl bg-slate-50 p-4">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />

              <span className="text-sm font-semibold">
                System Online
              </span>
            </div>

            <p className="mt-2 text-xs leading-5 text-slate-400">
              FastAPI and ML prediction services are operational.
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}