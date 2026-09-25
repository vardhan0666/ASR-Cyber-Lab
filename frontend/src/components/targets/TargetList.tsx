/**
 * Table/list of authorized targets with inline authorize/revoke,
 * edit, and deactivate actions. Action visibility is controlled by the
 * `canManage` prop, which pages set based on the current user's role.
 */

import Badge from "../common/Badge";
import Table from "../common/Table";
import type { Column } from "../common/Table";
import { formatDate, formatLabel } from "../../utils/format";
import type { Target } from "../../types";

interface TargetListProps {
  targets: Target[];
  canManage: boolean;
  onAuthorizeChange: (target: Target, isAuthorized: boolean) => void;
  onEdit: (target: Target) => void;
  onDeactivate: (target: Target) => void;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  onSortChange?: (key: string) => void;
}

export default function TargetList({
  targets,
  canManage,
  onAuthorizeChange,
  onEdit,
  onDeactivate,
  sortBy,
  sortOrder,
  onSortChange,
}: TargetListProps) {
  const columns: Column<Target>[] = [
    {
      key: "name",
      header: "Name",
      sortable: true,
      render: (t) => (
        <div>
          <p className="font-medium text-gray-900">{t.name}</p>
          <p className="text-xs text-gray-500">{t.address}</p>
        </div>
      ),
    },
    {
      key: "asset_importance",
      header: "Importance",
      sortable: true,
      render: (t) => (
        <Badge bg="bg-gray-100" text="text-gray-700" border="border-gray-300">
          {formatLabel(t.asset_importance)}
        </Badge>
      ),
    },
    {
      key: "is_authorized",
      header: "Authorization",
      render: (t) =>
        t.is_authorized ? (
          <Badge bg="bg-green-50" text="text-green-700" border="border-green-200">
            Authorized
          </Badge>
        ) : (
          <Badge bg="bg-gray-100" text="text-gray-600" border="border-gray-300">
            Not Authorized
          </Badge>
        ),
    },
    {
      key: "is_active",
      header: "Status",
      render: (t) =>
        t.is_active ? (
          <Badge bg="bg-blue-50" text="text-blue-700" border="border-blue-200">
            Active
          </Badge>
        ) : (
          <Badge bg="bg-gray-100" text="text-gray-500" border="border-gray-300">
            Inactive
          </Badge>
        ),
    },
    {
      key: "created_at",
      header: "Created",
      sortable: true,
      render: (t) => formatDate(t.created_at),
    },
    {
      key: "actions",
      header: "Actions",
      render: (t) => {
        if (!canManage || !t.is_active) {
          return <span className="text-xs text-gray-400">—</span>;
        }
        return (
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => onAuthorizeChange(t, !t.is_authorized)}
              className={`rounded border px-2 py-1 text-xs font-medium ${
                t.is_authorized
                  ? "border-amber-300 text-amber-700 hover:bg-amber-50"
                  : "border-green-300 text-green-700 hover:bg-green-50"
              }`}
            >
              {t.is_authorized ? "Revoke" : "Authorize"}
            </button>
            <button
              type="button"
              onClick={() => onEdit(t)}
              className="rounded border border-gray-300 px-2 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50"
            >
              Edit
            </button>
            <button
              type="button"
              onClick={() => onDeactivate(t)}
              className="rounded border border-red-300 px-2 py-1 text-xs font-medium text-red-700 hover:bg-red-50"
            >
              Deactivate
            </button>
          </div>
        );
      },
    },
  ];

  return (
    <Table
      columns={columns}
      data={targets}
      keyExtractor={(t) => t.id}
      sortBy={sortBy}
      sortOrder={sortOrder}
      onSortChange={onSortChange}
      emptyMessage="No targets found. Create one to get started."
    />
  );
}