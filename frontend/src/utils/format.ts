/**
 * Shared date/label/color formatting helpers used across dashboard,
 * target, scan, and finding views. Centralizing severity/status color
 * mappings here (rather than duplicating them per-component) keeps visual
 * meaning consistent throughout the platform.
 */

import type { FindingStatus, ScanStatus, SeverityLevel } from "../types";

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function capitalize(value: string): string {
  if (!value) return value;
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export function formatLabel(value: string): string {
  return value
    .split("_")
    .map((part) => capitalize(part))
    .join(" ");
}

export function formatRiskScore(score: number): string {
  return `${score.toFixed(1)}/100`;
}

export interface ColorClasses {
  bg: string;
  text: string;
  border: string;
}

const SEVERITY_COLOR_MAP: Record<SeverityLevel, ColorClasses> = {
  critical: {
    bg: "bg-red-100",
    text: "text-red-900",
    border: "border-red-300",
  },
  high: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200" },
  medium: {
    bg: "bg-amber-50",
    text: "text-amber-700",
    border: "border-amber-200",
  },
  low: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200" },
  info: {
    bg: "bg-gray-100",
    text: "text-gray-700",
    border: "border-gray-300",
  },
};

export function severityColorClasses(severity: SeverityLevel): ColorClasses {
  return SEVERITY_COLOR_MAP[severity] ?? SEVERITY_COLOR_MAP.info;
}

const SCAN_STATUS_COLOR_MAP: Record<ScanStatus, ColorClasses> = {
  pending: {
    bg: "bg-gray-100",
    text: "text-gray-700",
    border: "border-gray-300",
  },
  running: {
    bg: "bg-blue-50",
    text: "text-blue-700",
    border: "border-blue-200",
  },
  completed: {
    bg: "bg-green-50",
    text: "text-green-700",
    border: "border-green-200",
  },
  failed: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200" },
  cancelled: {
    bg: "bg-gray-100",
    text: "text-gray-600",
    border: "border-gray-300",
  },
};

export function scanStatusColorClasses(status: ScanStatus): ColorClasses {
  return SCAN_STATUS_COLOR_MAP[status] ?? SCAN_STATUS_COLOR_MAP.pending;
}

const FINDING_STATUS_COLOR_MAP: Record<FindingStatus, ColorClasses> = {
  open: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200" },
  acknowledged: {
    bg: "bg-amber-50",
    text: "text-amber-700",
    border: "border-amber-200",
  },
  resolved: {
    bg: "bg-green-50",
    text: "text-green-700",
    border: "border-green-200",
  },
  false_positive: {
    bg: "bg-gray-100",
    text: "text-gray-600",
    border: "border-gray-300",
  },
};

export function findingStatusColorClasses(status: FindingStatus): ColorClasses {
  return FINDING_STATUS_COLOR_MAP[status] ?? FINDING_STATUS_COLOR_MAP.open;
}