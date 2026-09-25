/** Reusable card container with an optional header row (title + actions). */

import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}

export default function Card({
  title,
  actions,
  children,
  className = "",
}: CardProps) {
  return (
    <div
      className={`rounded-lg border border-gray-200 bg-white shadow-sm ${className}`}
    >
      {(title || actions) && (
        <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
          {title && (
            <h2 className="text-sm font-semibold text-gray-900">{title}</h2>
          )}
          {actions && <div>{actions}</div>}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}