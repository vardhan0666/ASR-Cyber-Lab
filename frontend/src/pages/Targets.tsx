/**
 * Target management page: search, sortable listing, create/edit via a
 * modal form, explicit authorize/revoke actions, and soft-delete
 * (deactivate). Management actions are hidden entirely for viewer-role
 * users, mirroring the backend's role-gated endpoints.
 */

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { deactivateTarget, listTargets, setTargetAuthorization } from "../api/targets";
import { extractErrorMessage } from "../api/client";
import type { Target } from "../types";
import { useAuth } from "../hooks/useAuth";
import Card from "../components/common/Card";
import Loading from "../components/common/Loading";
import TargetForm from "../components/targets/TargetForm";
import TargetList from "../components/targets/TargetList";

type SortField = "name" | "address" | "created_at" | "asset_importance";

export default function Targets() {
  const { user } = useAuth();
  const canManage = user?.role === "admin" || user?.role === "analyst";

  const [targets, setTargets] = useState<Target[]>([]);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<SortField>("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingTarget, setEditingTarget] = useState<Target | undefined>(undefined);
  const [showForm, setShowForm] = useState(false);

  const fetchTargets = () => {
    setIsLoading(true);
    setError(null);
    listTargets({
      search: search || undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
      limit: 500,
    })
      .then(setTargets)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchTargets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortBy, sortOrder]);

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
    fetchTargets();
  };

  const handleAuthorizeChange = async (target: Target, isAuthorized: boolean) => {
    setError(null);
    try {
      await setTargetAuthorization(target.id, { is_authorized: isAuthorized });
      fetchTargets();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  const handleDeactivate = async (target: Target) => {
    const confirmed = window.confirm(
      `Deactivate target "${target.name}"? This will revoke its authorization.`,
    );
    if (!confirmed) return;

    setError(null);
    try {
      await deactivateTarget(target.id);
      fetchTargets();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  const handleFormSuccess = () => {
    setShowForm(false);
    setEditingTarget(undefined);
    fetchTargets();
  };

  return (
    <div className="space-y-4">
      <Card
        title="Authorized Targets"
        actions={
          canManage && (
            <button
              type="button"
              onClick={() => {
                setEditingTarget(undefined);
                setShowForm(true);
              }}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
            >
              New Target
            </button>
          )
        }
      >
        <form onSubmit={handleSearchSubmit} className="mb-4 flex items-end gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-500">Search</label>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Name or address..."
              className="mt-1 rounded-md border border-gray-300 px-2 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <button
            type="submit"
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
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
          <Loading label="Loading targets..." />
        ) : (
          <TargetList
            targets={targets}
            canManage={canManage}
            onAuthorizeChange={handleAuthorizeChange}
            onEdit={(target) => {
              setEditingTarget(target);
              setShowForm(true);
            }}
            onDeactivate={handleDeactivate}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onSortChange={handleSortChange}
          />
        )}
      </Card>

      {showForm && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-lg">
            <h2 className="mb-4 text-sm font-semibold text-gray-900">
              {editingTarget ? "Edit Target" : "New Target"}
            </h2>
            <TargetForm
              target={editingTarget}
              onSuccess={handleFormSuccess}
              onCancel={() => {
                setShowForm(false);
                setEditingTarget(undefined);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}