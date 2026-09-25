/**
 * Table/list of security findings. Reads a small set of common evidence
 * fields (ip_address, port) directly from the evidence JSON object where
 * present, since Finding.evidence is a free-form record mirroring
 * whatever the config analysis / scan orchestrator actually captured
 * (see backend/app/services/config_analysis_service.py).
 */

import { Link } from "react-router-dom";
import Badge from "../common/Badge";
import RiskBadge from "../common/RiskBadge";
import Table from "../common/Table";
import type { Column } from "../common/Table";
import { findingStatusColorClasses, formatDateTime, formatLabel } from "../../utils/format";
import type { Finding } from "../../types";

interface FindingListProps {
  findings: Finding[];
  showScanColumn?: boolean;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  onSortChange?: (key: string) => void;
}

function evidenceString(evidence: Record<string, unknown>, key: string): string | null {
  const value = evidence[key];
  return typeof value === "string" || typeof value === "number" ? String(value) : null;
}

export default function FindingList({
  findings,
  showScanColumn = true,
  sortBy,
  sortOrder,
  onSortChange,
}: FindingListProps) {
  const columns: Column<Finding>[] = [
    {
      key: "severity",
      header: "Severity",
      sortable: true,
      render: (f) => (
        <RiskBadge
          severity={f.severity}
          riskScore={f.risk_score}
          explanation={f.risk_explanation}
        />
      ),
    },
    {
      key: "title",
      header: "Finding",
      sortable: true,
      render: (f) => {
        const ip = evidenceString(f.evidence, "ip_address");
        const port = evidenceString(f.evidence, "port");
        return (
          <div>
            <p className="font-medium text-gray-900">{f.title}</p>
            {(ip || port) && (
              <p className="text-xs text-gray-500">
                {ip ?? ""}
                {ip && port ? ":" : ""}
                {port ?? ""}
              </p>
            )}
          </div>
        );
      },
    },
    {
      key: "category",
      header: "Category",
      render: (f) => formatLabel(f.category),
    },
    {
      key: "status",
      header: "Status",
      render: (f) => {
        const colors = findingStatusColorClasses(f.status);
        return <Badge {...colors}>{formatLabel(f.status)}</Badge>;
      },
    },
    ...(showScanColumn
      ? ([
          {
            key: "scan_id",
            header: "Scan",
            render: (f: Finding) => (
              <Link
                to={`/scans/${f.scan_id}`}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                View scan →
              </Link>
            ),
          },
        ] as Column<Finding>[])
      : []),
    {
      key: "created_at",
      header: "Discovered",
      sortable: true,
      render: (f) => formatDateTime(f.created_at),
    },
    {
      key: "actions",
      header: "",
      render: (f) => (
        <Link
          to={`/findings/${f.id}`}
          className="text-xs font-medium text-blue-600 hover:text-blue-800"
        >
          Details →
        </Link>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      data={findings}
      keyExtractor={(f) => f.id}
      sortBy={sortBy}
      sortOrder={sortOrder}
      onSortChange={onSortChange}
      emptyMessage="No findings match the current filters."
    />
  );
}