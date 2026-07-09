/**
 * OPTIONAL, READ-ONLY GET client for the local FastAPI dashboard API.
 *
 * This module is intentionally NOT imported by any page. The shell renders
 * committed fixtures by default so it needs no running backend and makes no
 * network contact. An operator may wire these helpers to a locally running
 * `tools.operator_dashboard_api` instance for live inspection.
 *
 * Boundary: this client issues `GET` requests only. It defines no POST/PUT/
 * PATCH/DELETE helper, no mutation, no Agent Inbox write, and no control call.
 * There is deliberately no generic `request(method, ...)` escape hatch.
 */

import type { ApiEnvelope } from "@/lib/types";

const DEFAULT_BASE_URL = "http://127.0.0.1:8000";

/** Read-only GET against the local dashboard API. */
async function getJson<T>(
  path: string,
  baseUrl: string = DEFAULT_BASE_URL,
): Promise<ApiEnvelope<T>> {
  const res = await fetch(`${baseUrl}${path}`, {
    method: "GET",
    cache: "no-store",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`GET ${path} failed with status ${res.status}`);
  }
  return (await res.json()) as ApiEnvelope<T>;
}

export const readOnlyApiClient = {
  dashboardSummary: () => getJson("/api/dashboard/summary"),
  researchJobs: () => getJson("/api/research/jobs"),
  resultPopulations: () => getJson("/api/research/result-populations"),
  resultPopulation: (id: string) =>
    getJson(`/api/research/result-populations/${encodeURIComponent(id)}`),
  strategies: () => getJson("/api/strategies"),
  strategy: (id: string) => getJson(`/api/strategies/${encodeURIComponent(id)}`),
  candidatesFunnel: () => getJson("/api/candidates/funnel"),
  reportsDaily: () => getJson("/api/reports/daily"),
  reportsWeekly: () => getJson("/api/reports/weekly"),
  systemDataHealth: () => getJson("/api/system/data-health"),
  agentIntakeSchema: () => getJson("/api/agent/intake-schema"),
};
