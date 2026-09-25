/**
 * Shared axios instance with authentication header injection, centralized
 * base URL configuration, and a consistent error-message extraction
 * helper. All api/*.ts modules import this client rather than creating
 * their own axios instances.
 */

import axios, { AxiosError } from "axios";

const API_BASE_URL = `${
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
}/api`;

export const TOKEN_STORAGE_KEY = "asr_access_token";

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredToken(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      clearStoredToken();
    }
    return Promise.reject(error);
  },
);

/**
 * Extracts a human-readable error message from an API error response.
 * Backend errors always take the shape { detail: string } (see
 * app.main.app_exception_handler and FastAPI's default validation error
 * shape), so this covers both cases plus a safe fallback.
 */
export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as
      | { detail?: string | { msg?: string }[] }
      | undefined;

    if (typeof data?.detail === "string") {
      return data.detail;
    }
    if (Array.isArray(data?.detail) && data.detail.length > 0) {
      return data.detail.map((d) => d.msg).filter(Boolean).join("; ");
    }
    if (error.message) {
      return error.message;
    }
  }
  return "An unexpected error occurred.";
}

export default apiClient;