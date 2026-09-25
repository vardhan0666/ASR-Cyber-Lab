/** Table/list of scans, resolving target names via a supplied targets list. */

import { Link } from "react-router-dom";
import Badge from "../common/Badge";
import Table from "../common/Table";
import type { Column } from "../common/Table";
import { formatDateTime, formatLabel, scanStatusColorClasses } from "../../utils/format";
import type { Scan, Target } from "../../types";

interface ScanListProps {
  scans: Scan[];
  targets?: Target[];
}

export default function ScanList({ scans, targets = [] }: ScanListProps) {
  const targetById = new Map(targets.map((t) => [t.id, t]));

  const columns: Column<Scan>[] = [
    {
      key: "target",
      header: "Target",
      render: (s) => {
        const target = targetById.get(s.target_id);
        return (
          <div>
            <p className="font-medium text-gray-900">
              {target ? target.name : s.target_id.slice(0, 8)}
            </p>
            {target && <p className="text-xs text-gray-500">{target.address}</p>}
          </div>
        );
      },
    },
    {
      key: "profile",
      header: "Profile",
      render: (s) => formatLabel(s.profile),
    },
    {
      key: "status",
      header: "Status",
      render: (s) => {
        const colors = scanStatusColorClasses(s.status);
        return <Badge {...colors}>{formatLabel(s.status)}</Badge>;
      },
    },
    {
      key: "created_at",
      header: "Created",
      sortable: true,
      render: (s) => formatDateTime(s.created_at),
    },
    {
      key: "completed_at",
      header: "Completed",
      render: (s) => formatDateTime(s.completed_at),
    },
    {
      key: "actions",
      header: "",
      render: (s) => (
        <Link
          to={`/scans/${s.id}`}
          className="text-xs font-medium text-blue-600 hover:text-blue-800"
        >
          View Details →
        </Link>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      data={scans}
      keyExtractor={(s) => s.id}
      emptyMessage="No scans found. Launch a scan against an authorized target to get started."
    />
  );
}