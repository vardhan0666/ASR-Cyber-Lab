/**
 * Risk-level badge with an on-hover/on-focus tooltip listing the risk
 * engine's full explanation array (EVIDENCE/INFERENCE/NOTE/RECOMMENDATION
 * lines), so the "why" behind every risk score is always one interaction
 * away rather than hidden.
 */

import { useState } from "react";
import type { SeverityLevel } from "../../types";
import { formatLabel, formatRiskScore, severityColorClasses } from "../../utils/format";
import Badge from "./Badge";

interface RiskBadgeProps {
  severity: SeverityLevel;
  riskScore?: number;
  explanation?: string[];
}

export default function RiskBadge({
  severity,
  riskScore,
  explanation,
}: RiskBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const colors = severityColorClasses(severity);
  const hasExplanation = Boolean(explanation && explanation.length > 0);

  return (
    <span className="relative inline-block">
      <span
        data-testid="risk-badge-trigger"
        onMouseEnter={() => hasExplanation && setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onFocus={() => hasExplanation && setShowTooltip(true)}
        onBlur={() => setShowTooltip(false)}
        tabIndex={hasExplanation ? 0 : -1}
      >
        <Badge {...colors}>
          {formatLabel(severity)}
          {riskScore !== undefined ? ` · ${formatRiskScore(riskScore)}` : ""}
        </Badge>
      </span>
      {showTooltip && hasExplanation && (
        <div
          role="tooltip"
          className="absolute z-10 mt-2 w-80 rounded-md border border-gray-200 bg-white p-3 text-xs text-gray-700 shadow-lg"
        >
          <p className="mb-1 font-semibold text-gray-900">Risk Explanation</p>
          <ul className="list-disc space-y-1 pl-4">
            {explanation!.map((line, index) => (
              <li key={index}>{line}</li>
            ))}
          </ul>
        </div>
      )}
    </span>
  );
}