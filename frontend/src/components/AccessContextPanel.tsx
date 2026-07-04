import type { AccessContextView } from "../types/query";

interface Props {
  accessContext: AccessContextView;
  filterApplied: Record<string, unknown>;
}

export function AccessContextPanel({ accessContext, filterApplied }: Props) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <h3 className="text-sm font-semibold text-slate-900">Access context</h3>
      <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-slate-600 sm:grid-cols-4">
        <dt className="font-medium text-slate-500">User</dt>
        <dd>{accessContext.user_id}</dd>
        <dt className="font-medium text-slate-500">Tenant</dt>
        <dd>{accessContext.tenant_id}</dd>
        <dt className="font-medium text-slate-500">Clearance</dt>
        <dd>{accessContext.clearance}</dd>
        <dt className="font-medium text-slate-500">ACL groups</dt>
        <dd>{accessContext.acl_groups.join(", ")}</dd>
      </dl>
      <details className="mt-3">
        <summary className="cursor-pointer text-xs font-medium text-slate-500">
          Filter applied to the vector query
        </summary>
        <pre className="mt-1 overflow-x-auto rounded bg-slate-50 p-2 text-xs text-slate-700">
          {JSON.stringify(filterApplied, null, 2)}
        </pre>
      </details>
    </div>
  );
}
