import { NavLink } from "react-router-dom";
import { useUser } from "../context/UserContext";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded-md text-sm font-medium ${
    isActive ? "bg-slate-900 text-white" : "text-slate-600 hover:bg-slate-100"
  }`;

export function NavBar() {
  const { selectedUser } = useUser();

  return (
    <nav className="flex items-center justify-between border-b border-slate-200 px-6 py-3">
      <div className="flex items-center gap-2">
        <span className="font-semibold text-slate-900">rag-platform</span>
        <NavLink to="/" className={linkClass} end>
          Users
        </NavLink>
        <NavLink to="/ask" className={linkClass}>
          Ask
        </NavLink>
        <NavLink to="/audit" className={linkClass}>
          Audit Log
        </NavLink>
      </div>
      <div className="text-sm text-slate-500">
        {selectedUser ? (
          <span>
            Signed in as <span className="font-medium text-slate-900">{selectedUser.display_name}</span>{" "}
            ({selectedUser.tenant_id})
          </span>
        ) : (
          <span>No user selected</span>
        )}
      </div>
    </nav>
  );
}
