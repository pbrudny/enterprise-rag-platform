import type { UserSummary } from "../types/user";

interface Props {
  user: UserSummary;
  selected: boolean;
  onSelect: (user: UserSummary) => void;
}

export function UserCard({ user, selected, onSelect }: Props) {
  return (
    <button
      type="button"
      onClick={() => onSelect(user)}
      className={`w-full rounded-lg border p-4 text-left transition ${
        selected
          ? "border-slate-900 ring-1 ring-slate-900"
          : "border-slate-200 hover:border-slate-400"
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-medium text-slate-900">{user.display_name}</span>
        <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">{user.role}</span>
      </div>
      <div className="mt-1 text-sm text-slate-500">
        {user.tenant_id} &middot; clearance: {user.clearance}
      </div>
      <div className="mt-2 flex flex-wrap gap-1">
        {user.acl_groups.map((group) => (
          <span key={group} className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
            {group}
          </span>
        ))}
      </div>
    </button>
  );
}
