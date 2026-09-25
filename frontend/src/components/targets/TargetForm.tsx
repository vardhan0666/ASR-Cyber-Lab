/**
 * Form to create a new authorized target, or edit an existing one.
 * Editing intentionally omits the address field: the backend's
 * TargetUpdate schema does not accept address changes (an address change
 * is treated as a materially different target and should be created
 * fresh), so the field is disabled rather than silently ignored.
 */

import { useState } from "react";
import type { FormEvent } from "react";
import { createTarget, updateTarget } from "../../api/targets";
import { extractErrorMessage } from "../../api/client";
import type { AssetImportance, Target } from "../../types";

interface TargetFormProps {
  target?: Target;
  onSuccess: (target: Target) => void;
  onCancel?: () => void;
}

const IMPORTANCE_OPTIONS: AssetImportance[] = ["low", "medium", "high", "critical"];

export default function TargetForm({ target, onSuccess, onCancel }: TargetFormProps) {
  const isEditMode = Boolean(target);

  const [name, setName] = useState(target?.name ?? "");
  const [address, setAddress] = useState(target?.address ?? "");
  const [description, setDescription] = useState(target?.description ?? "");
  const [assetImportance, setAssetImportance] = useState<AssetImportance>(
    target?.asset_importance ?? "medium",
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      let result: Target;
      if (isEditMode && target) {
        result = await updateTarget(target.id, {
          name,
          description: description || undefined,
          asset_importance: assetImportance,
        });
      } else {
        result = await createTarget({
          name,
          address,
          description: description || undefined,
          asset_importance: assetImportance,
        });
      }
      onSuccess(result);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">Name</label>
        <input
          type="text"
          required
          maxLength={255}
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="e.g. Lab Web Server"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Address (IPv4, IPv4 CIDR, or hostname)
        </label>
        <input
          type="text"
          required
          disabled={isEditMode}
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm disabled:bg-gray-100 disabled:text-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="e.g. 192.168.1.10 or 192.168.1.0/24"
        />
        {isEditMode && (
          <p className="mt-1 text-xs text-gray-500">
            Address cannot be changed after creation. Create a new target if
            the address has changed.
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Description (optional)
        </label>
        <textarea
          value={description ?? ""}
          onChange={(e) => setDescription(e.target.value)}
          rows={2}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Asset Importance
        </label>
        <select
          value={assetImportance}
          onChange={(e) => setAssetImportance(e.target.value as AssetImportance)}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          {IMPORTANCE_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-gray-500">
          Used directly by the risk engine to weight findings on this asset.
        </p>
      </div>

      {!isEditMode && (
        <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          New targets are created UNAUTHORIZED by default. You must
          explicitly authorize a target before any scan can run against it.
        </p>
      )}

      <div className="flex justify-end gap-2 pt-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting ? "Saving..." : isEditMode ? "Save Changes" : "Create Target"}
        </button>
      </div>
    </form>
  );
}