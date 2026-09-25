import apiClient from "./client";
import type {
  Target,
  TargetAuthorizeRequest,
  TargetCreate,
  TargetUpdate,
} from "../types";

export interface TargetListParams {
  search?: string;
  is_authorized?: boolean;
  is_active?: boolean;
  sort_by?: "name" | "address" | "created_at" | "asset_importance";
  sort_order?: "asc" | "desc";
  skip?: number;
  limit?: number;
}

export async function listTargets(
  params: TargetListParams = {},
): Promise<Target[]> {
  const response = await apiClient.get<Target[]>("/targets", { params });
  return response.data;
}

export async function getTarget(id: string): Promise<Target> {
  const response = await apiClient.get<Target>(`/targets/${id}`);
  return response.data;
}

export async function createTarget(payload: TargetCreate): Promise<Target> {
  const response = await apiClient.post<Target>("/targets", payload);
  return response.data;
}

export async function updateTarget(
  id: string,
  payload: TargetUpdate,
): Promise<Target> {
  const response = await apiClient.patch<Target>(`/targets/${id}`, payload);
  return response.data;
}

export async function setTargetAuthorization(
  id: string,
  payload: TargetAuthorizeRequest,
): Promise<Target> {
  const response = await apiClient.post<Target>(
    `/targets/${id}/authorize`,
    payload,
  );
  return response.data;
}

export async function deactivateTarget(id: string): Promise<void> {
  await apiClient.delete(`/targets/${id}`);
}