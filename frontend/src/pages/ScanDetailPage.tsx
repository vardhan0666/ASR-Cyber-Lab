/**
 * Single scan detail page. Polls for updates every 5 seconds while the
 * scan is pending/running, and stops polling automatically once the scan
 * reaches a terminal status (completed/failed/cancelled).
 */

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getScan } from "../api/scans";
import { extractErrorMessage } from "../api/client";
import type { Scan } from "../types";
import Loading from "../components/common/Loading";
import ScanDetail from "../components/scans/ScanDetail";

const POLL_INTERVAL_MS = 5000;

export default function ScanDetailPage() {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();

  const [scan, setScan] = useState<Scan | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!scanId) return;

    let isMounted = true;
    let intervalId: ReturnType<typeof setInterval> | undefined;

    const fetchScan = () => {
      getScan(scanId)
        .then((result) => {
          if (!isMounted) return;
          setScan(result);
          setError(null);
          if (
            (result.status === "completed" ||
              result.status === "failed" ||
              result.status === "cancelled") &&
            intervalId
          ) {
            clearInterval(intervalId);
          }
        })
        .catch((err) => isMounted && setError(extractErrorMessage(err)))
        .finally(() => isMounted && setIsLoading(false));
    };

    fetchScan();
    intervalId = setInterval(fetchScan, POLL_INTERVAL_MS);

    return () => {
      isMounted = false;
      if (intervalId) clearInterval(intervalId);
    };
  }, [scanId]);

  if (isLoading) {
    return <Loading label="Loading scan..." />;
  }

  if (error || !scan) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => navigate("/scans")}
          className="text-sm text-blue-600 hover:underline"
        >
          ← Back to scans
        </button>
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error ?? "Scan not found."}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <button
        onClick={() => navigate("/scans")}
        className="text-sm text-blue-600 hover:underline"
      >
        ← Back to scans
      </button>
      <ScanDetail scan={scan} />
    </div>
  );
}