/**
 * Generic, reusable, sortable data table. Column definitions carry their
 * own render function, so this component has no knowledge of the specific
 * domain models (Target/Scan/Finding/etc.) it will be used to display.
 *
 * Deliberately implemented as a `function Table<T>(...)` declaration
 * rather than an arrow function: TypeScript's generic arrow function
 * syntax (`const Table = <T,>(...) => ...`) is ambiguous with JSX tags in
 * .tsx files and requires an awkward trailing-comma workaround, which a
 * plain generic function declaration avoids entirely.
 */

import type { ReactNode } from "react";

export interface Column<T> {
  key: string;
  header: string;
  sortable?: boolean;
  render: (row: T) => ReactNode;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T) => string;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  onSortChange?: (key: string) => void;
  emptyMessage?: string;
}

export default function Table<T>({
  columns,
  data,
  keyExtractor,
  sortBy,
  sortOrder,
  onSortChange,
  emptyMessage = "No data available.",
}: TableProps<T>) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col) => {
              const isActive = sortBy === col.key;
              return (
                <th
                  key={col.key}
                  scope="col"
                  className={`px-4 py-2 text-left font-medium text-gray-500 ${
                    col.sortable
                      ? "cursor-pointer select-none hover:text-gray-700"
                      : ""
                  }`}
                  onClick={() => col.sortable && onSortChange?.(col.key)}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.header}
                    {col.sortable && isActive && (
                      <span>{sortOrder === "asc" ? "▲" : "▼"}</span>
                    )}
                  </span>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {data.length === 0 && (
            <tr>
              <td
                colSpan={columns.length}
                className="px-4 py-6 text-center text-gray-400"
              >
                {emptyMessage}
              </td>
            </tr>
          )}
          {data.map((row) => (
            <tr key={keyExtractor(row)} className="hover:bg-gray-50">
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-2 text-gray-700">
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}