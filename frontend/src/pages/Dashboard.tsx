/**
 * Security dashboard: platform-wide summary counts, a findings-by-severity
 * chart, recent scan activity, and an explicit transparency note about
 * the scope of the local CVE reference dataset.
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getDashboardSummary } from "../api/dashboard";
import { extractErrorMessage } from "../api/client";
import type { DashboardSummary } from "../types";
import { formatDateTime, formatLabel, scanStatusColorClasses } from "../utils/format";
import Badge from "../components/common/Badge";
import Card from "../components/common/Card";
import Loading from "../components/common/Loading";

const SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"] as const;
const SEVERITY_CHART_COLORS: Record<string, string> = {
  critical: "#7f1d1d",
  high: "#b91c1c",
  medium: "#b45309",
  low: "#1d4ed8",
  info: "#374151",
};

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    getDashboardSummary()
      .then((data) => isMounted && setSummary(data))
      .catch((err) => isMounted && setError(extractErrorMessage(err)))
      .finally(() => isMounted && setIsLoading(false));
    return () => {
      isMounted = false;
    };
  }, []);

  if (isLoading) {
    return <Loading label="Loading dashboard..." />;
  }

  if (error || !summary) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
        {error ?? "Unable to load dashboard summary."}
      </div>
    );
  }

  const chartData = SEVERITY_ORDER.map((level) => ({
    severity: formatLabel(level),
    count: summary.findings_by_severity[level] ?? 0,
    fill: SEVERITY_CHART_COLORS[level],
  }));

  const summaryCards: { label: string; value: number }[] = [
    { label: "Total Targets", value: summary.total_targets },
    { label: "Authorized Targets", value: summary.authorized_targets },
    { label: "Total Scans", value: summary.total_scans },
    { label: "Scans In Progress", value: summary.scans_in_progress },
    { label: "Hosts Discovered", value: summary.total_hosts },
    { label: "Total Findings", value: summary.total_findings },
  ];

  return (
    <div className="space-y-6">
      {summary.cve_data_availability_note && (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          {summary.cve_data_availability_note}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        {summaryCards.map((card) => (
          <Card key={card.label}>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
              {card.label}
            </p>
            <p className="mt-1 text-2xl font-bold text-gray-900">{card.value}</p>
          </Card>
        ))}
      </div>

      <Card title="Findings by Severity">
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="severity" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card title="Recent Scans">
        {summary.recent_scans.length === 0 ? (
          <p className="text-sm text-gray-500">No scans have been run yet.</p>
        ) : (
          <div className="divide-y divide-gray-100">
            {summary.recent_scans.map((scan) => {
              const colors = scanStatusColorClasses(scan.status);
              return (
                <div
                  key={scan.id}
                  className="flex items-center justify-between py-2 text-sm"
                >
                  <div>
                    <p className="font-medium text-gray-900">{scan.target_name}</p>
                    <p className="text-xs text-gray-500">
                      {formatDateTime(scan.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge {...colors}>{formatLabel(scan.status)}</Badge>
                    <Link
                      to={`/scans/${scan.id}`}
                      className="text-xs font-medium text-blue-600 hover:text-blue-800"
                    >
                      View →
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
}