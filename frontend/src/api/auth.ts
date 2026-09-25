import apiClient from "./client";
import type { CurrentUser, LoginRequest, TokenResponse, UserCreate, User } from "../types";

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/auth/login", payload);
  return response.data;
}

export async function getCurrentUser(): Promise<CurrentUser> {
  const response = await apiClient.get<CurrentUser>("/auth/me");
  return response.data;
}

export async function registerUser(payload: UserCreate): Promise<User> {
  const response = await apiClient.post<User>("/auth/register", payload);
  return response.data;
}