export interface AuditEvent {
  timestamp: string;
  event_type: string;
  details: Record<string, unknown>;
}
