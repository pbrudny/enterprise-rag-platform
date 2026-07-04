import axios from "axios";
import type { AuditEvent } from "../types/audit";
import type { DocumentIngestResponse } from "../types/document";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function postDocument(formData: FormData): Promise<DocumentIngestResponse> {
  const { data } = await axios.post<DocumentIngestResponse>(
    `${BASE_URL}/api/documents`,
    formData,
  );
  return data;
}

export async function getDocumentActivity(userId: string): Promise<AuditEvent[]> {
  const { data } = await axios.get<AuditEvent[]>(`${BASE_URL}/api/documents/activity`, {
    params: { user_id: userId },
  });
  return data;
}
