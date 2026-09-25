/**
 * ASR-Cyber-Lab login page.
 *
 * Authentication logic remains unchanged; only the presentation
 * has been redesigned.
 */

import { useState } from "react";
import type { FormEvent } from "react";
import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import { extractErrorMessage } from "../api/client";
import { useAuth } from "../hooks/useAuth";

interface LocationState {
  from?: {
    pathname: string;
  };
}

export default function Login() {
  const { login } = useAuth();

  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const handleSubmit = async (
    event: FormEvent,
  ) => {
    event.preventDefault();

    setError(null);
    setIsSubmitting(true);

    try {
      await login(email, password);

      const state =
        location.state as LocationState | null;

      navigate(
        state?.from?.pathname ?? "/",
        { replace: true },
      );
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="asr-login-shell">
      <div
        className="asr-login-grid"
        aria-hidden="true"
      />

      <div
        className="pointer-events-none absolute left-1/2 top-1/2 z-0 h-[520px] w-[520px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-400/5"
        aria-hidden="true"
      >
        <div className="absolute inset-8 rounded-full border border-cyan-400/5" />
        <div className="absolute inset-20 rounded-full border border-cyan-400/5" />
      </div>

      <div className="asr-login-panel">
        <div className="mb-8">
          <div className="flex items-center gap-3">
            <div className="asr-brand-mark">
              <span className="text-xs font-black">
                ASR
              </span>
            </div>

            <div>
              <div className="text-sm font-black tracking-[0.16em] text-white">
                ASR-CYBER-LAB
              </div>

              <div className="mt-1 text-[9px] uppercase tracking-[0.18em] text-slate-600">
                Security Command Center
              </div>
            </div>
          </div>

          <div className="mt-7">
            <div className="flex items-center gap-2">
              <span className="asr-system-dot" />

              <span className="text-[9px] uppercase tracking-[0.2em] text-cyan-400">
                Secure Console
              </span>
            </div>

            <h1 className="mt-3 text-2xl font-semibold tracking-tight text-white">
              Operator authentication
            </h1>

            <p className="mt-2 text-xs leading-5 text-slate-500">
              Authorized defensive security testing only.
            </p>
          </div>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-5"
        >
          {error && (
            <div className="rounded-xl border border-rose-400/20 bg-rose-400/[0.05] px-3 py-3 text-xs text-rose-300">
              <div className="mb-1 text-[9px] font-semibold uppercase tracking-[0.15em] text-rose-400">
                Authentication Error
              </div>

              {error}
            </div>
          )}

          <div>
            <label
              htmlFor="email"
              className="block text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-500"
            >
              Operator Email
            </label>

            <input
              id="email"
              type="email"
              required
              autoComplete="username"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              className="mt-2 block w-full rounded-xl border px-3.5 py-3 text-sm"
              data-cursor="interactive"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-500"
            >
              Access Credential
            </label>

            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              className="mt-2 block w-full rounded-xl border px-3.5 py-3 text-sm"
              data-cursor="interactive"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-xl border border-cyan-300/30 bg-cyan-400/[0.09] px-4 py-3 text-xs font-semibold uppercase tracking-[0.16em] text-cyan-200 hover:border-cyan-300/55 hover:bg-cyan-400/[0.14] disabled:cursor-not-allowed disabled:opacity-50"
            data-cursor="interactive"
          >
            {isSubmitting
              ? "Authenticating..."
              : "Initialize Console"}
          </button>
        </form>

        <div className="mt-7 border-t border-cyan-400/8 pt-4">
          <div className="flex items-center justify-between text-[9px] uppercase tracking-[0.13em] text-slate-700">
            <span>Session Security</span>
            <span className="text-emerald-400/75">
              Protected
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}