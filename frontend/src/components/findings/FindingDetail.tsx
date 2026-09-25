/**
 * Detailed finding evidence/risk view: raw evidence, the full risk-engine
 * explanation trail, remediation guidance, associated vulnerability
 * (CVE) enrichment results, and a triage-status control. Vulnerability
 * data is fetched internally so this component can be dropped into a
 * page with only a Finding object.
 */

import { useEffect, useState } from "react";
import {
  listFindingVulnerabilities,
  updateFindingStatus,
} from "../../api/findings";
import { extractErrorMessage } from "../../api/client";
import type { Finding, FindingStatus, Vulnerability } from "../../types";
import { findingStatusColorClasses, formatDateTime, formatLabel } from "../../utils/format";
import Badge from "../common/Badge";
import Card from "../common/Card";
import Loading from "../common/Loading";
import RiskBadge from "../common/RiskBadge";

interface FindingDetailProps {
  finding: Finding;
  canManage: boolean;
  onStatusChange?: (updated: Finding) => void;
}

const STATUS_OPTIONS: FindingStatus[] = [
  "open",
  "acknowledged",
  "resolved",
  "false_positive",
];

export default function FindingDetail({
  finding,
  canManage,
  onStatusChange,
}: FindingDetailProps) {
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [isLoadingVulns, setIsLoadingVulns] = useState(true);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    listFindingVulnerabilities(finding.id)
      .then((results) => isMounted && setVulnerabilities(results))
      .catch((err) => isMounted && setError(extractErrorMessage(err)))
      .finally(() => isMounted && setIsLoadingVulns(false));
    return () => {
      isMounted = false;
    };
  }, [finding.id]);

  const handleStatusChange = async (status: FindingStatus) => {
    setIsUpdatingStatus(true);
    setError(null);
    try {
      const updated = await updateFindingStatus(finding.id, { status });
      onStatusChange?.(updated);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const statusColors = findingStatusColorClasses(finding.status);

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="mb-2 flex items-center gap-2">
              <RiskBadge
                severity={finding.severity}
                riskScore={finding.risk_score}
                explanation={finding.risk_explanation}
              />
              <Badge {...statusColors}>{formatLabel(finding.status)}</Badge>
            </div>
            <h1 className="text-lg font-semibold text-gray-900">{finding.title}</h1>
            <p className="mt-1 text-sm text-gray-600">{finding.description}</p>
            <p className="mt-2 text-xs text-gray-400">
              Category: {formatLabel(finding.category)} · Discovered{" "}
              {formatDateTime(finding.created_at)}
            </p>
          </div>

          {canManage && (
            <div className="flex flex-col gap-1">
              <label className="text-xs font-medium text-gray-500">
                Update Status
              </label>
              <select
                value={finding.status}
                disabled={isUpdatingStatus}
                onChange={(e) => handleStatusChange(e.target.value as FindingStatus)}
                className="rounded-md border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {STATUS_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {formatLabel(option)}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </Card>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <Card title="Risk Explanation">
        <ul className="list-disc space-y-1.5 pl-5 text-sm text-gray-700">
          {finding.risk_explanation.map((line, index) => (
            <li key={index}>{line}</li>
          ))}
        </ul>
      </Card>

      <Card title="Evidence">
        <pre className="overflow-x-auto rounded-md bg-gray-900 p-3 text-xs text-gray-100">
          {JSON.stringify(finding.evidence, null, 2)}
        </pre>
      </Card>

      {finding.remediation && (
        <Card title="Remediation">
          <p className="text-sm text-gray-700">{finding.remediation}</p>
        </Card>
      )}

      <Card title="Vulnerability Enrichment">
        {isLoadingVulns ? (
          <Loading label="Loading vulnerability data..." />
        ) : vulnerabilities.length === 0 ? (
          <p className="text-sm text-gray-500">
            No vulnerability enrichment was attempted for this finding.
          </p>
        ) : (
          <div className="space-y-3">
            {vulnerabilities.map((v) => (
              <div
                key={v.id}
                className={`rounded-md border px-3 py-2 text-sm ${
                  v.data_available
                    ? "border-red-200 bg-red-50"
                    : "border-gray-200 bg-gray-50"
                }`}
              >
                {v.data_available ? (
                  <>
                    <p className="font-medium text-gray-900">
                      {v.cve_id}{" "}
                      {v.cvss_score !== null && (
                        <span className="text-xs text-gray-500">
                          (CVSS {v.cvss_score.toFixed(1)})
                        </span>
                      )}
                    </p>
                    <p className="mt-1 text-xs text-gray-600">{v.description}</p>
                    {v.reference_url && (
                      <a
                        href={v.reference_url}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-1 inline-block text-xs text-blue-600 hover:underline"
                      >
                        Reference →
                      </a>
                    )}
                  </>
                ) : (
                  <p className="text-xs text-gray-600">
                    <span className="font-medium text-gray-900">
                      Vulnerability data unavailable.
                    </span>{" "}
                    {v.description}
                  </p>
                )}
                <p className="mt-1 text-[10px] uppercase tracking-wide text-gray-400">
                  Source: {v.source}
                </p>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}