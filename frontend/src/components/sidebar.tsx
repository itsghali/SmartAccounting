"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  CalendarDays,
  LayoutDashboard,
  Building2,
  BookOpen,
  FileText,
  PenLine,
  Scale,
  BookText,
  PieChart,
  BarChart3,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Tableau de bord", icon: LayoutDashboard },
  { href: "/dossiers", label: "Dossiers", icon: Building2 },
  { href: "/exercices", label: "Exercices", icon: CalendarDays },
  { href: "/plan-comptable", label: "Plan comptable", icon: BookOpen },
  { href: "/journaux", label: "Journaux", icon: FileText },
  { href: "/ecritures", label: "Ecritures", icon: PenLine },
  { href: "/balance", label: "Balance generale", icon: Scale },
  { href: "/grand-livre", label: "Grand livre", icon: BookText },
  { href: "/bilan", label: "Bilan", icon: PieChart },
  { href: "/cpc", label: "CPC", icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-brand-900 text-white flex flex-col min-h-screen">
      <div className="p-6">
        <h1 className="text-xl font-bold">EasyAccounting</h1>
        <p className="text-brand-100 text-xs mt-1">ERP SaaS Marocain</p>
      </div>
      <nav className="flex-1 px-3">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm mb-1 transition-colors",
                isActive
                  ? "bg-white/15 text-white"
                  : "text-white/70 hover:bg-white/10 hover:text-white"
              )}
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-3 border-t border-white/10">
        <Link
          href="/settings"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-white/70 hover:bg-white/10"
        >
          <Settings className="w-5 h-5" />
          Paramètres
        </Link>
      </div>
    </aside>
  );
}
