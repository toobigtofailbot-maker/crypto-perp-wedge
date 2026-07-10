/**
 * Application layout: sidebar + global status header + scrollable content.
 *
 * On narrow/mobile viewports the shell stacks vertically — the sidebar becomes
 * a full-width nav block above the content — so the content column keeps the
 * full viewport width instead of being crushed beside a fixed sidebar. From the
 * `md` breakpoint up it is the persistent side-by-side sidebar layout.
 */
import type { ReactNode } from "react";
import { Sidebar } from "@/components/Sidebar";
import { StatusHeader } from "@/components/StatusHeader";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen w-full flex-col overflow-x-hidden bg-cockpit-bg md:h-screen md:flex-row md:overflow-hidden">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <StatusHeader />
        <main className="flex-1 px-4 py-6 md:overflow-y-auto md:px-6">
          <div className="mx-auto flex max-w-5xl flex-col gap-5">{children}</div>
        </main>
      </div>
    </div>
  );
}
