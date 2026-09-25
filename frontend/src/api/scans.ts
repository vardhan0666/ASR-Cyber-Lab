import apiClient from "./client";
import type { Host, Scan, ScanCreate, ScanStatus } from "../types";

export interface ScanListParams {
  target_id?: string;
  status?: ScanStatus;
  skip?: number;
  limit?: number;
}

export async function listScans(params: ScanListParams = {}): Promise<Scan[]> {
  const response = await apiClient.get<Scan[]>("/scans", { params });
  return response.data;
}

export async function getScan(id: string): Promise<Scan> {
  const response = await apiClient.get<Scan>(`/scans/${id}`);
  return response.data;
}

export async function createScan(payload: ScanCreate): Promise<Scan> {
  const response = await apiClient.post<Scan>("/scans", payload);
  return response.data;
}

/**
 * Fetches the discovered host/port inventory for a scan via the shared
 * /hosts endpoint (see backend/app/api/routes/hosts.py), filtered by
 * scan_id. Kept here rather than in a separate hosts.ts module since host
 * data is only ever browsed in the context of a specific scan in this
 * frontend (no standalone host-browsing page is planned).
 */
export async function getScanHosts(scanId: string): Promise<Host[]> {
  const response = await apiClient.get<Host[]>("/hosts", {
    params: { scan_id: scanId, limit: 500 },
  });
  return response.data;
}