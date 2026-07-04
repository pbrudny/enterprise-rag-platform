import type { AuditEvent } from "../types/audit";

interface Props {
  events: AuditEvent[];
}

export function AuditEventsTable({ events }: Props) {
  if (events.length === 0) {
    return <p className="text-sm text-slate-500">No audit events yet.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-left text-xs font-medium uppercase text-slate-500">
          <tr>
            <th className="px-3 py-2">Timestamp</th>
            <th className="px-3 py-2">Event type</th>
            <th className="px-3 py-2">Details</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {events.map((event, i) => (
            <tr key={`${event.timestamp}-${i}`}>
              <td className="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-500">
                {event.timestamp}
              </td>
              <td className="px-3 py-2 font-medium text-slate-800">{event.event_type}</td>
              <td className="max-w-md truncate px-3 py-2 font-mono text-xs text-slate-600">
                <details>
                  <summary className="cursor-pointer truncate">
                    {JSON.stringify(event.details)}
                  </summary>
                  <pre className="mt-1 max-w-md overflow-x-auto whitespace-pre-wrap break-all">
                    {JSON.stringify(event.details, null, 2)}
                  </pre>
                </details>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
