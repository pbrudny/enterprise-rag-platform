export interface AccessContextView {
  user_id: string;
  tenant_id: string;
  clearance: string;
  acl_groups: string[];
}

export interface RetrievedChunkView {
  chunk_id: string;
  doc_id: string;
  tenant_id: string;
  acl_group: string;
  classification: string;
  title: string;
  text: string;
  score: number;
}

export interface QueryRequest {
  user_id: string;
  question: string;
  k?: number;
}

export interface QueryResponse {
  access_context: AccessContextView;
  filter_applied: Record<string, unknown>;
  injection_detected: boolean;
  injection_matched_patterns: string[];
  chunks: RetrievedChunkView[];
  answer: string;
  citations: string[];
  sufficient_context: boolean;
  validation_passed: boolean;
  validation_reason: string | null;
}
