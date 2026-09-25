/**
 * Reports page: generate a JSON/PDF report for a completed scan
 * (analyst/admin only) and browse/download previously generated reports.
 * Downloads are fetched as a Blob (since the endpoint requires an
 * Authorization header) and saved via a programmatically-triggered
 * object-URL link.
 */

import { useEffect, useState } from "react";
import { downloadReport, generateReport, listReports } from "../api/reports";
import { listScans } from "../api/scans";
import { extractErrorMessage } from "../api/client";
import type { Report, ReportFormat, Scan } from "../types";
import { useAuth } from "../hooks/useAuth";
import { formatDateTime, formatLabel } from "../utils/format";
import Card from "../components/common/Card";
import Loading from "../components/common/Loading";
import Table from "../components/common/Table";
import type { Column } from "../components/common/Table";

export default function Reports() {
  const { user } = useAuth();
  const canGenerate = user?.role === "admin" || user?.role === "analyst";

  const [reports, setReports] = useState<Report[]>([]);
  const [scans, setScans] = useState<Scan[]>([]);
  const [selectedScanId, setSelectedScanId] = useState("");
  const [format, setFormat] = useState<ReportFormat>("json");
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = () => {
    setIsLoading(true);
    setError(null);
    Promise.all([
      listReports({ limit: 200 }),
      listScans({ status: "completed", limit: 200 }),
    ])
      .then(([reportResults, scanResults]) => {
        setReports(reportResults);
        setScans(scanResults);
        setSelectedScanId((current) => current || scanResults[0]?.id || "");
      })
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleGenerate = async () => {
    if (!selectedScanId) {
      setError("Select a completed scan to generate a report for.");
      return;
    }
    setIsGenerating(true);
    setError(null);
    try {
      await generateReport({ scan_id: selectedScanId, format });
      fetchData();
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async (report: Report) => {
    setError(null);
    try {
      const blob = await downloadReport(report.id);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      const fallbackName = `report_${report.id}.${report.format}`;
      link.download = report.file_path
        ? report.file_path.split(/[\\/]/).pop() ?? fallbackName
        : fallbackName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  const columns: Column<Report>[] = [
    { key: "format", header: "Format", render: (r) => formatLabel(r.format) },
    { key: "scan_id", header: "Scan", render: (r) => r.scan_id.slice(0, 8) },
    { key: "created_at", header: "Generated", render: (r) => formatDateTime(r.created_at) },
    {
      key: "actions",
      header: "",
      render: (r) => (
        <button
          type="button"
          onClick={() => handleDownload(r)}
          className="text-xs font-medium text-blue-600 hover:text-blue-800"
        >
          Download
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      {canGenerate && (
        <Card title="Generate Report">
          <div className="flex flex-wrap items-end gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-500">
                Completed Scan
              </label>
              <select
                value={selectedScanId}
                onChange={(e) => setSelectedScanId(e.target.value)}
                className="mt-1 rounded-md border border-gray-300 px-2 py-1.5 text-sm"
              >
                {scans.length === 0 && (
                  <option value="">No completed scans available</option>
                )}
                {scans.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.id.slice(0, 8)} — {formatDateTime(s.completed_at)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500">Format</label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value as ReportFormat)}
                className="mt-1 rounded-md border border-gray-300 px-2 py-1.5 text-sm"
              >
                <option value="json">JSON</option>
                <option value="pdf">PDF</option>
              </select>
            </div>
            <button
              type="button"
              onClick={handleGenerate}
              disabled={isGenerating || scans.length === 0}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {isGenerating ? "Generating..." : "Generate Report"}
            </button>
          </div>
        </Card>
      )}

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <Card title="Generated Reports">
        {isLoading ? (
          <Loading label="Loading reports..." />
        ) : (
          <Table
            columns={columns}
            data={reports}
            keyExtractor={(r) => r.id}
            emptyMessage="No reports generated yet."
          />
        )}
      </Card>
    </div>
  );
}