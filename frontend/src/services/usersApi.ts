import axios from "axios";
import type { UserSummary } from "../types/user";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function getUsers(): Promise<UserSummary[]> {
  const { data } = await axios.get<UserSummary[]>(`${BASE_URL}/api/users`);
  return data;
}
