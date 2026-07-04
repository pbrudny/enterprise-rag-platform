export interface DocumentIngestResponse {
  doc_id: string;
  title: string;
  tenant_id: string;
  acl_group: string;
  classification: string;
}

export interface QuarantinedError {
  message: string;
  matched_patterns: string[];
}
