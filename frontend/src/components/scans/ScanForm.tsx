/**
 * Form to launch a new scan against an authorized, active target. Only
 * targets that are both authorized and active are offered — this mirrors
 * (and provides a friendlier UX layer over) the backend's own
 * authorization enforcement in scan_orchestrator.create_scan.
 */

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { listTargets } from "../../api/targets";
import { createScan } from "../../api/scans";
import { extractErrorMessage } from "../../api/client";
import type { Scan, ScanProfile, Target } from "../../types";
import Loading from "../common/Loading";

interface ScanFormProps {
  onSuccess: (scan: Scan) => void;
  onCancel?: () => void;
  presetTargetId?: string;
}

const PROFILE_OPTIONS: { value: ScanProfile; label: string; description: string }[] = [
  { value: "quick", label: "Quick", description: "Fast scan of the 100 most common ports." },
  {
    value: "standard",
    label: "Standard",
    description: "Top 1000 ports with service/version detection.",
  },
  { value: "full_tcp", label: "Full TCP", description: "All 65535 TCP ports with service detection." },
  {
    value: "version_detection",
    label: "Version Detection",
    description: "Top 1000 ports focused on service/version fingerprinting.",
  },
  { value: "os_detection", label: "OS Detection", description: "Top 1000 ports plus OS fingerprinting." },
];

export default function ScanForm({ onSuccess, onCancel, presetTargetId }: ScanFormProps) {
  const [targets, setTargets] = useState<Target[]>([]);
  const [isLoadingTargets, setIsLoadingTargets] = useState(true);
  const [targetId, setTargetId] = useState(presetTargetId ?? "");
  const [profile, setProfile] = useState<ScanProfile>("standard");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    listTargets({ is_authorized: true, is_active: true, limit: 500 })
      .then((results) => {
        if (isMounted) {
          setTargets(results);
          if (!presetTargetId && results.length > 0) {
            setTargetId(results[0].id);
          }
        }
      })
      .catch((err) => isMounted && setError(extractErrorMessage(err)))
      .finally(() => isMounted && setIsLoadingTargets(false));
    return () => {
      isMounted = false;
    };
  }, [presetTargetId]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!targetId) {
      setError("Select an authorized target before launching a scan.");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      const scan = await createScan({ target_id: targetId, profile });
      onSuccess(scan);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingTargets) {
    return <Loading label="Loading authorized targets..." />;
  }

  if (targets.length === 0) {
    return (
      <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
        No authorized, active targets are available. Authorize a target
        before launching a scan.
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">Target</label>
        <select
          value={targetId}
          disabled={Boolean(presetTargetId)}
          onChange={(e) => setTargetId(e.target.value)}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm disabled:bg-gray-100 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          {targets.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name} ({t.address})
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Scan Profile</label>
        <div className="mt-2 space-y-2">
          {PROFILE_OPTIONS.map((option) => (
            <label
              key={option.value}
              className={`flex cursor-pointer items-start gap-3 rounded-md border px-3 py-2 text-sm ${
                profile === option.value
                  ? "border-blue-400 bg-blue-50"
                  : "border-gray-200 hover:bg-gray-50"
              }`}
            >
              <input
                type="radio"
                name="profile"
                value={option.value}
                checked={profile === option.value}
                onChange={() => setProfile(option.value)}
                className="mt-1"
              />
              <span>
                <span className="block font-medium text-gray-900">{option.label}</span>
                <span className="block text-xs text-gray-500">{option.description}</span>
              </span>
            </label>
          ))}
        </div>
      </div>

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
          {isSubmitting ? "Launching..." : "Launch Scan"}
        </button>
      </div>
    </form>
  );
}