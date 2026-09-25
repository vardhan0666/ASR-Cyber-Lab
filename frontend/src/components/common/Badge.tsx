/**
 * Generic colored status badge. Accepts explicit bg/text/border Tailwind
 * class strings (matching the ColorClasses shape from utils/format.ts) so
 * callers can spread severity/status color mappings directly, e.g.
 * <Badge {...severityColorClasses(finding.severity)}>High</Badge>.
 */

import type { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  bg?: string;
  text?: string;
  border?: string;
  className?: string;
}

export default function Badge({
  children,
  bg = "bg-gray-100",
  text = "text-gray-700",
  border = "border-gray-300",
  className = "",
}: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${bg} ${text} ${border} ${className}`}
    >
      {children}
    </span>
  );
}