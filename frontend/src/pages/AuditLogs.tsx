/**
 * Audit log page. Administrator-only (enforced both by the router's
 * role-gated ProtectedRoute and, authoritatively, by the backend's
 * admin-only /audit-logs endpoint). Fetches audit data directly via the
 * shared apiClient rather than a dedicated api/audit_logs.ts module, since
 * this page is the sole frontend consumer of that endpoint.
 */

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import apiClient, { extractErrorMessage } from "../api/client";
import type { AuditLog } from "../types";
import { formatDateTime } from "../utils/format";
import Card from "../components/common/Card";
import Loading from "../components/common/Loading";
import Table from "../components/common/Table";
import type { Column } from "../components/common/Table";

async function fetchAuditLogs(params: { action?: string }): Promise<AuditLog[]> {
  const response = await apiClient.get<AuditLog[]>("/audit-logs", {
    params: { ...params, limit: 200 },
  });
  return response.data;
}

export default function AuditLogs() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [actionFilter, setActionFilter] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setIsLoading(true);
    setError(null);
    fetchAuditLogs({ action: actionFilter || undefined })
      .then(setLogs)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSearchSubmit = (event: FormEvent) => {
    event.preventDefault();
    load();
  };

  const columns: Column<AuditLog>[] = [
    { key: "created_at", header: "Timestamp", render: (l) => formatDateTime(l.created_at) },
    { key: "action", header: "Action", render: (l) => l.action },
    {
      key: "resource_type",
      header: "Resource Type",
      render: (l) => l.resource_type ?? "—",
    },
    { key: "resource_id", header: "Resource ID", render: (l) => l.resource_id ?? "—" },
    {
      key: "user_id",
      header: "User ID",
      render: (l) => (l.user_id ? l.user_id.slice(0, 8) : "system"),
    },
    { key: "ip_address", header: "IP Address", render: (l) => l.ip_address ?? "—" },
  ];

  return (
    <Card title="Audit Log">
      <form onSubmit={handleSearchSubmit} className="mb-4 flex items-end gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-500">Action</label>
          <input
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            placeholder="e.g. target.created"
            className="mt-1 rounded-md border border-gray-300 px-2 py-1.5 text-sm"
          />
        </div>
        <button
          type="submit"
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          Filter
        </button>
      </form>

      {error && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {isLoading ? (
        <Loading label="Loading audit logs..." />
      ) : (
        <Table
          columns={columns}
          data={logs}
          keyExtractor={(l) => l.id}
          emptyMessage="No audit log entries found."
        />
      )}
    </Card>
  );
}