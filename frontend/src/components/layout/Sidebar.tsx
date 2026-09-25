/**
 * Primary ASR-Cyber-Lab navigation.
 *
 * Audit Logs remains administrator-only, matching the existing
 * frontend/backend authorization design.
 */

import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

interface NavItem {
  to: string;
  label: string;
  end?: boolean;
  icon: ReactNode;
}

function DashboardIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <rect x="3" y="3" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.7" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.7" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.7" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

function TargetIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.7" />
      <circle cx="12" cy="12" r="4.5" stroke="currentColor" strokeWidth="1.7" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" />
    </svg>
  );
}

function ScanIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path d="M5 7V5a2 2 0 0 1 2-2h2" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M15 3h2a2 2 0 0 1 2 2v2" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M19 17v2a2 2 0 0 1-2 2h-2" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M9 21H7a2 2 0 0 1-2-2v-2" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <path d="M5 12h14" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

function FindingIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M12 3.5 20 18H4L12 3.5Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path d="M12 9v4.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <circle cx="12" cy="16.5" r="0.8" fill="currentColor" />
    </svg>
  );
}

function ReportIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M6 3.5h8l4 4V20.5H6V3.5Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path d="M14 3.5v4h4" stroke="currentColor" strokeWidth="1.7" />
      <path d="M9 12h6M9 15.5h6" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

function AuditIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M5 4h14v16H5z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path d="M8.5 8h7M8.5 12h7M8.5 16h4" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

const NAV_ITEMS: NavItem[] = [
  {
    to: "/",
    label: "Dashboard",
    end: true,
    icon: <DashboardIcon />,
  },
  {
    to: "/targets",
    label: "Targets",
    icon: <TargetIcon />,
  },
  {
    to: "/scans",
    label: "Scans",
    icon: <ScanIcon />,
  },
  {
    to: "/findings",
    label: "Findings",
    icon: <FindingIcon />,
  },
  {
    to: "/reports",
    label: "Reports",
    icon: <ReportIcon />,
  },
];

function NavItemLink({
  item,
}: {
  item: NavItem;
}) {
  return (
    <NavLink
      to={item.to}
      end={item.end}
      className={({ isActive }) =>
        `asr-nav-item ${
          isActive ? "asr-nav-item-active" : ""
        }`
      }
      data-cursor="interactive"
    >
      <span className="shrink-0">
        {item.icon}
      </span>

      <span className="flex-1">
        {item.label}
      </span>
    </NavLink>
  );
}

export default function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="asr-sidebar hidden h-full flex-shrink-0 flex-col lg:flex">
      <div className="px-5 pb-4 pt-5">
        <div className="flex items-center gap-3">
          <div className="asr-brand-mark">
            <span className="text-xs font-black">
              ASR
            </span>
          </div>

          <div className="min-w-0">
            <div className="truncate text-sm font-bold tracking-[0.14em] text-white">
              ASR-CYBER-LAB
            </div>

            <div className="mt-0.5 text-[9px] uppercase tracking-[0.18em] text-slate-500">
              Security Command Center
            </div>
          </div>
        </div>
      </div>

      <div className="mx-4 h-px bg-cyan-400/10" />

      <div className="px-4 py-5">
        <div className="mb-2 px-2 text-[9px] font-semibold uppercase tracking-[0.2em] text-slate-600">
          Operations
        </div>

        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => (
            <NavItemLink
              item={item}
              key={item.to}
            />
          ))}

          {user?.role === "admin" && (
            <NavLink
              to="/audit-logs"
              className={({ isActive }) =>
                `asr-nav-item ${
                  isActive ? "asr-nav-item-active" : ""
                }`
              }
              data-cursor="interactive"
            >
              <span className="shrink-0">
                <AuditIcon />
              </span>

              <span className="flex-1">
                Audit Logs
              </span>
            </NavLink>
          )}
        </nav>
      </div>

      <div className="mt-auto p-4">
        <div className="rounded-xl border border-cyan-400/10 bg-cyan-400/[0.025] p-3">
          <div className="flex items-center gap-2">
            <span className="asr-system-dot" />

            <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-cyan-200">
              System Online
            </span>
          </div>

          <div className="mt-2 text-[10px] leading-5 text-slate-600">
            Authorized defensive security testing only.
          </div>
        </div>
      </div>
    </aside>
  );
}