/**
 * Findings page. Handles both routes /findings (list with filters) and
 * /findings/:findingId (single finding detail) from a single component,
 * switching behavior based on the presence of the findingId route param —
 * this keeps the page count aligned with the original file plan (no
 * separate FindingDetailPage was allocated).
 */

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getFinding, listFindings } from "../api/findings";
import { extractErrorMessage } from "../api/client";
import type {
  Finding,
  FindingCategory,
  FindingStatus,
  SeverityLevel,
} from "../types";
import { useAuth } from "../hooks/useAuth";
import Card from "../components/common/Card";
import Loading from "../components/common/Loading";
import FindingDetail from "../components/findings/FindingDetail";
import FindingList from "../components/findings/FindingList";

const SEVERITY_OPTIONS: SeverityLevel[] = ["critical", "high", "medium", "low", "info"];
const CATEGORY_OPTIONS: FindingCategory[] = ["configuration", "vulnerability", "exposure"];
const STATUS_OPTIONS: FindingStatus[] = [
  "open",
  "acknowledged",
  "resolved",
  "false_positive",
];

type SortField = "risk_score" | "created_at" | "severity" | "title";

export default function Findings() {
  const { findingId } = useParams<{ findingId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const canManage = user?.role === "admin" || user?.role === "analyst";

  if (findingId) {
    return (
      <FindingDetailView
        findingId={findingId}
        canManage={canManage}
        onBack={() => navigate("/findings")}
      />
    );
  }

  return <FindingListView />;
}

interface FindingDetailViewProps {
  findingId: string;
  canManage: boolean;
  onBack: () => void;
}

function FindingDetailView({ findingId, canManage, onBack }: FindingDetailViewProps) {
  const [finding, setFinding] = useState<Finding | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    getFinding(findingId)
      .then((result) => isMounted && setFinding(result))
      .catch((err) => isMounted && setError(extractErrorMessage(err)))
      .finally(() => isMounted && setIsLoading(false));
    return () => {
      isMounted = false;
    };
  }, [findingId]);

  if (isLoading) {
    return <Loading label="Loading finding..." />;
  }

  if (error || !finding) {
    return (
      <div className="space-y-4">
        <button onClick={onBack} className="text-sm text-blue-600 hover:underline">
          ← Back to findings
        </button>
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error ?? "Finding not found."}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <button onClick={onBack} className="text-sm text-blue-600 hover:underline">
        ← Back to findings
      </button>
      <FindingDetail finding={finding} canManage={canManage} onStatusChange={setFinding} />
    </div>
  );
}

function FindingListView() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState<SeverityLevel | "">("");
  const [category, setCategory] = useState<FindingCategory | "">("");
  const [status, setStatus] = useState<FindingStatus | "">("");
  const [sortBy, setSortBy] = useState<SortField>("risk_score");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const fetchFindings = () => {
    setIsLoading(true);
    setError(null);
    listFindings({
      search: search || undefined,
      severity: severity || undefined,
      category: category || undefined,
      status: status || undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
      limit: 200,
    })
      .then(setFindings)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchFindings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [severity, category, status, sortBy, sortOrder]);

  const handleSortChange = (key: string) => {
    if (key === sortBy) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(key as SortField);
      setSortOrder("desc");
    }
  };

  const handleSearchSubmit = (event: FormEvent) => {
    event.preventDefault();
    fetchFindings();
  };

  return (
    <Card title="Security Findings">
      <form onSubmit={handleSearchSubmit} className="mb-4 flex flex-wrap items-end gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-500">Search</label>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Finding title..."
            className="mt-1 rounded-md border border-gray-300 px-2 py-1.5 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">Severity</label>
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value as SeverityLevel | "")}
            className="mt-1 rounded-md border border-gray-300 px-2 py-1.5 text-sm"
          >
            <option value="">All</option>
            {SEVERITY_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">Category</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value as FindingCategory | "")}
            className="mt-1 rounded-md border border-gray-300 px-2 py-1.5 text-sm"
          >
            <option value="">All</option>
            {CATEGORY_OPTIONS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">Status</label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as FindingStatus | "")}
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
          type="submit"
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          Search
        </button>
      </form>

      {error && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {isLoading ? (
        <Loading label="Loading findings..." />
      ) : (
        <FindingList
          findings={findings}
          sortBy={sortBy}
          sortOrder={sortOrder}
          onSortChange={handleSortChange}
        />
      )}
    </Card>
  );
}