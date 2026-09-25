/**
 * ASR-Cyber-Lab command header.
 */

import { useLocation } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

const ROUTE_LABELS: Record<string, string> = {
  "/": "Security Dashboard",
  "/targets": "Asset Targets",
  "/scans": "Scan Operations",
  "/findings": "Security Findings",
  "/reports": "Security Reports",
  "/audit-logs": "Audit Trail",
};

export default function Header() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const pageLabel =
    ROUTE_LABELS[location.pathname] ??
    (location.pathname.startsWith("/scans/")
      ? "Scan Intelligence"
      : location.pathname.startsWith("/findings/")
        ? "Finding Intelligence"
        : "Security Operations");

  return (
    <header className="asr-header flex flex-shrink-0 items-center justify-between px-4 sm:px-6">
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-[9px] uppercase tracking-[0.2em] text-slate-600">
            ASR
          </span>

          <span className="text-[9px] text-slate-700">
            /
          </span>

          <span className="truncate text-[9px] uppercase tracking-[0.2em] text-cyan-400/80">
            {pageLabel}
          </span>
        </div>

        <div className="mt-1 flex items-center gap-2">
          <span className="asr-system-dot" />

          <span className="text-xs font-medium text-slate-300">
            Defensive Monitoring Active
          </span>
        </div>
      </div>

      {user && (
        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <div className="text-xs font-semibold text-slate-200">
              {user.full_name}
            </div>

            <div className="mt-0.5 text-[9px] uppercase tracking-[0.18em] text-slate-600">
              {user.role}
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-xl border border-cyan-400/10 bg-cyan-400/[0.025] px-2.5 py-1.5">
            <span className="asr-system-dot" />

            <span className="text-[9px] uppercase tracking-[0.14em] text-cyan-300">
              Online
            </span>
          </div>

          <button
            type="button"
            onClick={logout}
            className="rounded-lg border border-slate-700/70 bg-slate-900/55 px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-400 hover:border-cyan-400/25 hover:text-cyan-200"
            data-cursor="interactive"
          >
            Log out
          </button>
        </div>
      )}
    </header>
  );
}