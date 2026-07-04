import { createContext, useContext, useState, type ReactNode } from "react";
import type { UserSummary } from "../types/user";

interface UserContextValue {
  selectedUser: UserSummary | null;
  setSelectedUser: (user: UserSummary | null) => void;
}

const UserContext = createContext<UserContextValue | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [selectedUser, setSelectedUser] = useState<UserSummary | null>(null);
  return (
    <UserContext.Provider value={{ selectedUser, setSelectedUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser(): UserContextValue {
  const ctx = useContext(UserContext);
  if (!ctx) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return ctx;
}
