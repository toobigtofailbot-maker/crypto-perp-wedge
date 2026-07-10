"use client";

/**
 * Sidebar navigation. Interactivity is navigation-only: it reads the current
 * pathname to highlight the active route. It fires no action and mutates no
 * state beyond client-side routing via Next.js <Link>.
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_GROUPS } from "@/lib/nav";

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function Sidebar() {
  const pathname = usePathname() ?? "/";

  return (
    <nav
      className="flex w-full shrink-0 flex-col gap-4 border-b border-cockpit-border bg-cockpit-panel px-3 py-4 md:h-full md:w-60 md:gap-6 md:overflow-y-auto md:border-b-0 md:border-r"
      aria-label="Primary"
    >
      <div className="px-2">
        <div className="text-sm font-semibold tracking-wide text-cockpit-heading">
          Operator Dashboard
        </div>
        <div className="text-[11px] uppercase tracking-wider text-cockpit-accent">
          Local · Read-only shell
        </div>
      </div>

      <ul className="flex flex-row flex-wrap gap-x-1 gap-y-1 md:flex-col">
        {NAV_GROUPS.map((group) => {
          const active = isActive(pathname, group.href);
          return (
            <li key={group.href} className="flex flex-col">
              <Link
                href={group.href}
                className={`rounded px-2 py-1.5 text-sm ${
                  active
                    ? "bg-cockpit-panel-2 font-medium text-cockpit-heading"
                    : "text-cockpit-muted hover:text-cockpit-text"
                }`}
              >
                {group.label}
              </Link>
              {group.items && active ? (
                <ul className="ml-3 mt-1 flex flex-col gap-0.5 border-l border-cockpit-border pl-2">
                  {group.items.map((item) => (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        className={`block rounded px-2 py-1 text-xs ${
                          isActive(pathname, item.href)
                            ? "text-cockpit-accent"
                            : "text-cockpit-muted hover:text-cockpit-text"
                        }`}
                      >
                        {item.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              ) : null}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
