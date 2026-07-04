export interface UserSummary {
  user_id: string;
  tenant_id: string;
  display_name: string;
  role: string;
  clearance: string;
  acl_groups: string[];
}
