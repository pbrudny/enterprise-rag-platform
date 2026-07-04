import axios from "axios";
import type { QueryRequest, QueryResponse } from "../types/query";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function postQuery(req: QueryRequest): Promise<QueryResponse> {
  const { data } = await axios.post<QueryResponse>(`${BASE_URL}/api/query`, req);
  return data;
}
