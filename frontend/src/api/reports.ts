import apiClient from "./client";
import type { Report, ReportGenerateRequest } from "../types";

export interface ReportListParams {
  scan_id?: string;
  skip?: number;
  limit?: number;
}

export async function generateReport(
  payload: ReportGenerateRequest,
): Promise<Report> {
  const response = await apiClient.post<Report>("/reports", payload);
  return response.data;
}

export async function listReports(
  params: ReportListParams = {},
): Promise<Report[]> {
  const response = await apiClient.get<Report[]>("/reports", { params });
  return response.data;
}

export async function getReport(id: string): Promise<Report> {
  const response = await apiClient.get<Report>(`/reports/${id}`);
  return response.data;
}

/**
 * Downloads the report file as a Blob. A direct <a href> link cannot be
 * used because the download endpoint requires an Authorization header;
 * callers should create an object URL from the returned Blob (e.g.
 * `URL.createObjectURL(blob)`) and trigger a download programmatically.
 */
export async function downloadReport(id: string): Promise<Blob> {
  const response = await apiClient.get(`/reports/${id}/download`, {
    responseType: "blob",
  });
  return response.data;
}