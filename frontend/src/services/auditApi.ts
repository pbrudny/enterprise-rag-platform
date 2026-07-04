import axios from "axios";
import type { AuditEvent } from "../types/audit";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function getAudit(n = 50): Promise<AuditEvent[]> {
  const { data } = await axios.get<AuditEvent[]>(`${BASE_URL}/api/audit`, { params: { n } });
  return data;
}
