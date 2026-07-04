import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UserCard } from "../components/UserCard";
import { useUser } from "../context/UserContext";
import { getUsers } from "../services/usersApi";
import type { UserSummary } from "../types/user";

export function UserPickerPage() {
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const { selectedUser, setSelectedUser } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    getUsers()
      .then(setUsers)
      .catch(() => setError("Failed to load users. Is the API running (uv run rag serve)?"));
  }, []);

  function handleSelect(user: UserSummary) {
    setSelectedUser(user);
    navigate("/ask");
  }

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h1 className="text-xl font-semibold text-slate-900">Pick a mock user</h1>
      <p className="mt-1 text-sm text-slate-500">
        No real authentication — this mirrors the CLI's <code>--user</code> flag. Tenant, ACL
        groups, and clearance are resolved from the selected user for every question you ask.
      </p>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {users.map((user) => (
          <UserCard
            key={user.user_id}
            user={user}
            selected={selectedUser?.user_id === user.user_id}
            onSelect={handleSelect}
          />
        ))}
      </div>
    </div>
  );
}
