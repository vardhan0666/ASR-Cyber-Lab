/**
 * Scan history page: status filtering, a launch-scan modal (analyst/admin
 * only), and a manual refresh control (scans run asynchronously in the
 * background, so there is no push-based status update).
 */

import { useEffect, useState } from "react";
import { listScans } from "../api/scans";
import { listTargets } from "../api/targets";
import { extractErrorMessage } from "../api/client";
import type { Scan, ScanStatus, Target } from "../types";
import { useAuth } from "../hooks/useAuth";
import Card from "../components/common/Card";
import Loading from "../components/common/Loading";
import ScanForm from "../components/scans/ScanForm";
import ScanList from "../components/scans/ScanList";

const STATUS_OPTIONS: ScanStatus[] = [
  "pending",
  "running",
  "completed",
  "failed",
  "cancelled",
];

export default function Scans() {
  const { user } = useAuth();
  const canLaunch = user?.role === "admin" || user?.role === "analyst";

  const [scans, setScans] = useState<Scan[]>([]);
  const [targets, setTargets] = useState<Target[]>([]);
  const [statusFilter, setStatusFilter] = useState<ScanStatus | "">("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const fetchData = () => {
    setIsLoading(true);
    setError(null);
    Promise.all([
      listScans({ status: statusFilter || undefined, limit: 200 }),
      listTargets({ limit: 500 }),
    ])
      .then(([scanResults, targetResults]) => {
        setScans(scanResults);
        setTargets(targetResults);
      })
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  return (
    <div className="space-y-4">
      <Card
        title="Scan History"
        actions={
          canLaunch && (
            <button
              type="button"
              onClick={() => setShowForm(true)}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
            >
              Launch Scan
            </button>
          )
        }
      >
        <div className="mb-4 flex items-end gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-500">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as ScanStatus | "")}
              className="mt-1 rounded-md border border-gray-300 px-2 py-1.5 text-sm"
            >
              <option value="">All</option>
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            onClick={fetchData}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Refresh
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        {isLoading ? (
          <Loading label="Loading scans..." />
        ) : (
          <ScanList scans={scans} targets={targets} />
        )}
      </Card>

      {showForm && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-lg">
            <h2 className="mb-4 text-sm font-semibold text-gray-900">
              Launch New Scan
            </h2>
            <ScanForm
              onSuccess={() => {
                setShowForm(false);
                fetchData();
              }}
              onCancel={() => setShowForm(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}