/**
 * Convenience hook for consuming AuthContext. Throws a clear error if used
 * outside of an AuthProvider, catching a common integration mistake early
 * (at component render time) rather than surfacing a confusing undefined
 * property error later.
 */

import { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import type { AuthContextValue } from "../context/AuthContext";

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}