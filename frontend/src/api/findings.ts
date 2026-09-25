import apiClient from "./client";
import type {
  Finding,
  FindingCategory,
  FindingStatus,
  FindingStatusUpdate,
  SeverityLevel,
  Vulnerability,
} from "../types";

export interface FindingListParams {
  scan_id?: string;
  host_id?: string;
  severity?: SeverityLevel;
  category?: FindingCategory;
  status?: FindingStatus;
  search?: string;
  sort_by?: "risk_score" | "created_at" | "severity" | "title";
  sort_order?: "asc" | "desc";
  skip?: number;
  limit?: number;
}

export async function listFindings(
  params: FindingListParams = {},
): Promise<Finding[]> {
  const response = await apiClient.get<Finding[]>("/findings", { params });
  return response.data;
}

export async function getFinding(id: string): Promise<Finding> {
  const response = await apiClient.get<Finding>(`/findings/${id}`);
  return response.data;
}

export async function updateFindingStatus(
  id: string,
  payload: FindingStatusUpdate,
): Promise<Finding> {
  const response = await apiClient.patch<Finding>(
    `/findings/${id}/status`,
    payload,
  );
  return response.data;
}

/**
 * Fetches CVE enrichment results for a single finding via the shared
 * /vulnerabilities endpoint (see backend/app/api/routes/vulnerabilities.py),
 * filtered by finding_id. Kept here rather than in a separate
 * vulnerabilities.ts module since vulnerability data is only ever viewed
 * in the context of a specific finding in this frontend.
 */
export async function listFindingVulnerabilities(
  findingId: string,
): Promise<Vulnerability[]> {
  const response = await apiClient.get<Vulnerability[]>("/vulnerabilities", {
    params: { finding_id: findingId, limit: 100 },
  });
  return response.data;
}