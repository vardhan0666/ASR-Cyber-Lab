/**
 * Detailed scan results view: scan metadata, discovered host/port
 * inventory, and a findings summary for the scan. Fetches its own host
 * and finding data given a scan, so it can be reused directly from
 * ScanDetailPage (Batch 12) without that page needing to know about
 * fetching internals.
 */

import { useEffect, useState } from "react";
import { getScanHosts } from "../../api/scans";
import { listFindings } from "../../api/findings";
import { extractErrorMessage } from "../../api/client";
import type { Finding, Host, Scan } from "../../types";
import { formatDateTime, formatLabel, scanStatusColorClasses } from "../../utils/format";
import Badge from "../common/Badge";
import Card from "../common/Card";
import Loading from "../common/Loading";
import FindingList from "../findings/FindingList";

interface ScanDetailProps {
  scan: Scan;
}

export default function ScanDetail({ scan }: ScanDetailProps) {
  const [hosts, setHosts] = useState<Host[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    Promise.all([getScanHosts(scan.id), listFindings({ scan_id: scan.id })])
      .then(([hostResults, findingResults]) => {
        if (isMounted) {
          setHosts(hostResults);
          setFindings(findingResults);
        }
      })
      .catch((err) => isMounted && setError(extractErrorMessage(err)))
      .finally(() => isMounted && setIsLoading(false));
    return () => {
      isMounted = false;
    };
  }, [scan.id]);

  const statusColors = scanStatusColorClasses(scan.status);

  return (
    <div className="space-y-6">
      <Card title="Scan Overview">
        <dl className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
          <div>
            <dt className="text-gray-500">Status</dt>
            <dd className="mt-1">
              <Badge {...statusColors}>{formatLabel(scan.status)}</Badge>
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Profile</dt>
            <dd className="mt-1 font-medium text-gray-900">{formatLabel(scan.profile)}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Started</dt>
            <dd className="mt-1 font-medium text-gray-900">
              {formatDateTime(scan.started_at)}
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Completed</dt>
            <dd className="mt-1 font-medium text-gray-900">
              {formatDateTime(scan.completed_at)}
            </dd>
          </div>
        </dl>
        {scan.status === "failed" && scan.error_message && (
          <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            Scan failed: {scan.error_message}
          </p>
        )}
        {(scan.status === "pending" || scan.status === "running") && (
          <p className="mt-4 rounded-md border border-blue-200 bg-blue-50 px-3 py-2 text-sm text-blue-700">
            This scan is still in progress. Refresh the page to check for
            updated results.
          </p>
        )}
      </Card>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {isLoading ? (
        <Loading label="Loading scan results..." />
      ) : (
        <>
          <Card title={`Discovered Hosts (${hosts.length})`}>
            {hosts.length === 0 ? (
              <p className="text-sm text-gray-500">
                No hosts were discovered during this scan.
              </p>
            ) : (
              <div className="space-y-4">
                {hosts.map((host) => (
                  <div key={host.id} className="rounded-md border border-gray-200 p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">
                          {host.ip_address}
                          {host.hostname && (
                            <span className="ml-2 text-xs text-gray-500">
                              ({host.hostname})
                            </span>
                          )}
                        </p>
                        <p className="text-xs text-gray-500">
                          OS:{" "}
                          {host.os_name
                            ? `${host.os_name}${
                                host.os_accuracy ? ` (${host.os_accuracy}% confidence)` : ""
                              }`
                            : "Not determined"}
                        </p>
                      </div>
                    </div>
                    {host.port_services.length > 0 ? (
                      <table className="mt-3 min-w-full text-xs">
                        <thead>
                          <tr className="text-left text-gray-500">
                            <th className="pr-4 py-1">Port</th>
                            <th className="pr-4 py-1">Protocol</th>
                            <th className="pr-4 py-1">State</th>
                            <th className="pr-4 py-1">Service</th>
                            <th className="pr-4 py-1">Product</th>
                            <th className="pr-4 py-1">Version</th>
                          </tr>
                        </thead>
                        <tbody>
                          {host.port_services.map((port) => (
                            <tr key={port.id} className="border-t border-gray-100">
                              <td className="pr-4 py-1">{port.port_number}</td>
                              <td className="pr-4 py-1">{port.protocol}</td>
                              <td className="pr-4 py-1">{port.state}</td>
                              <td className="pr-4 py-1">{port.service_name ?? "—"}</td>
                              <td className="pr-4 py-1">{port.product ?? "—"}</td>
                              <td className="pr-4 py-1">{port.version ?? "—"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <p className="mt-2 text-xs text-gray-400">No ports reported.</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card title={`Findings (${findings.length})`}>
            <FindingList findings={findings} showScanColumn={false} />
          </Card>
        </>
      )}
    </div>
  );
}