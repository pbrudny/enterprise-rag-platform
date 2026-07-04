import { useEffect, useState } from "react";
import { AuditEventsTable } from "../components/AuditEventsTable";
import { getAudit } from "../services/auditApi";
import type { AuditEvent } from "../types/audit";

export function AuditLogPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const data = await getAudit(50);
      // newest first, mirrors `rag audit tail`
      setEvents([...data].reverse());
    } catch {
      setError("Failed to load audit log. Is the API running (uv run rag serve)?");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-4 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900">Audit log</h1>
        <button
          type="button"
          onClick={refresh}
          disabled={loading}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <AuditEventsTable events={events} />
    </div>
  );
}
