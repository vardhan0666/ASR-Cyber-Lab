/**
 * Shared TypeScript types mirroring the backend's Pydantic response/request
 * schemas exactly (see backend/app/schemas/*). Keeping these in sync is
 * critical: any drift here is a source of silent frontend/backend contract
 * mismatches.
 */

// ---------------------------------------------------------------------------
// Enums (string literal unions matching backend Python enums)
// ---------------------------------------------------------------------------

export type UserRole = "admin" | "analyst" | "viewer";

export type AssetImportance = "low" | "medium" | "high" | "critical";

export type ScanProfile =
  | "quick"
  | "standard"
  | "full_tcp"
  | "version_detection"
  | "os_detection";

export type ScanStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

export type FindingCategory = "configuration" | "vulnerability" | "exposure";

export type FindingStatus =
  | "open"
  | "acknowledged"
  | "resolved"
  | "false_positive";

export type SeverityLevel = "info" | "low" | "medium" | "high" | "critical";

export type ReportFormat = "json" | "pdf";

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export type CurrentUser = User;

export interface UserCreate {
  email: string;
  full_name: string;
  role: UserRole;
  password: string;
}

// ---------------------------------------------------------------------------
// Targets
// ---------------------------------------------------------------------------

export interface Target {
  id: string;
  name: string;
  address: string;
  description: string | null;
  asset_importance: AssetImportance;
  is_authorized: boolean;
  is_active: boolean;
  authorized_by_id: string | null;
  authorized_at: string | null;
  created_by_id: string;
  created_at: string;
  updated_at: string;
}

export interface TargetCreate {
  name: string;
  address: string;
  description?: string;
  asset_importance?: AssetImportance;
}

export interface TargetUpdate {
  name?: string;
  description?: string;
  asset_importance?: AssetImportance;
  is_active?: boolean;
}

export interface TargetAuthorizeRequest {
  is_authorized: boolean;
}

// ---------------------------------------------------------------------------
// Scans
// ---------------------------------------------------------------------------

export interface Scan {
  id: string;
  target_id: string;
  initiated_by_id: string;
  profile: ScanProfile;
  status: ScanStatus;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface ScanCreate {
  target_id: string;
  profile: ScanProfile;
}

// ---------------------------------------------------------------------------
// Hosts / Ports
// ---------------------------------------------------------------------------

export interface PortService {
  id: string;
  host_id: string;
  port_number: number;
  protocol: string;
  state: string;
  service_name: string | null;
  product: string | null;
  version: string | null;
  extra_info: string | null;
  created_at: string;
}

export interface Host {
  id: string;
  scan_id: string;
  ip_address: string;
  hostname: string | null;
  status: string;
  os_name: string | null;
  os_accuracy: number | null;
  mac_address: string | null;
  created_at: string;
  port_services: PortService[];
}

// ---------------------------------------------------------------------------
// Findings
// ---------------------------------------------------------------------------

export interface Finding {
  id: string;
  scan_id: string;
  host_id: string | null;
  port_service_id: string | null;
  category: FindingCategory;
  title: string;
  description: string;
  evidence: Record<string, unknown>;
  severity: SeverityLevel;
  risk_score: number;
  risk_explanation: string[];
  status: FindingStatus;
  remediation: string | null;
  created_at: string;
  updated_at: string;
}

export interface FindingStatusUpdate {
  status: FindingStatus;
}

// ---------------------------------------------------------------------------
// Vulnerabilities
// ---------------------------------------------------------------------------

export interface Vulnerability {
  id: string;
  finding_id: string;
  cve_id: string | null;
  source: string;
  description: string | null;
  cvss_score: number | null;
  severity: SeverityLevel | null;
  reference_url: string | null;
  data_available: boolean;
  created_at: string;
}

// ---------------------------------------------------------------------------
// Reports
// ---------------------------------------------------------------------------

export interface Report {
  id: string;
  scan_id: string;
  generated_by_id: string;
  format: ReportFormat;
  file_path: string | null;
  created_at: string;
}

export interface ReportGenerateRequest {
  scan_id: string;
  format: ReportFormat;
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export interface RecentScanSummary {
  id: string;
  target_name: string;
  status: ScanStatus;
  created_at: string;
}

export interface DashboardSummary {
  total_targets: number;
  authorized_targets: number;
  total_scans: number;
  scans_in_progress: number;
  total_hosts: number;
  total_findings: number;
  findings_by_severity: Record<string, number>;
  recent_scans: RecentScanSummary[];
  cve_data_availability_note: string | null;
}

// ---------------------------------------------------------------------------
// Audit Logs
// ---------------------------------------------------------------------------

export interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  details: string | null;
  ip_address: string | null;
  created_at: string;
}

// ---------------------------------------------------------------------------
// AI
// ---------------------------------------------------------------------------

export interface AIStatusResponse {
  enabled: boolean;
  note: string;
}

export interface AIExplainResponse {
  finding_id: string;
  available: boolean;
  summary: string | null;
  note: string;
  evidence_used: Record<string, unknown>;
}