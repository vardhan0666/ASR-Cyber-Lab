import apiClient from "./client";
import type { DashboardSummary } from "../types";

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await apiClient.get<DashboardSummary>("/dashboard/summary");
  return response.data;
}