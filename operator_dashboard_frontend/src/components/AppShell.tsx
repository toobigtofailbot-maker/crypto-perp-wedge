/** Application layout: sidebar + global status header + scrollable content. */
import type { ReactNode } from "react";
import { Sidebar } from "@/components/Sidebar";
import { StatusHeader } from "@/components/StatusHeader";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-cockpit-bg">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <StatusHeader />
        <main className="flex-1 overflow-y-auto px-6 py-6">
          <div className="mx-auto flex max-w-5xl flex-col gap-5">{children}</div>
        </main>
      </div>
    </div>
  );
}
