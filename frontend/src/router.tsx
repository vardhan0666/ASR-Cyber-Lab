/**
 * Application route tree. Uses react-router v6's pathless "layout route"
 * pattern: ProtectedRoute and Layout each contribute no path segment of
 * their own, so nested relative paths ("targets", "scans", etc.) resolve
 * to the same absolute paths already used throughout Sidebar's NavLinks.
 */

import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/common/ProtectedRoute";
import Layout from "./components/layout/Layout";
import AuditLogs from "./pages/AuditLogs";
import Dashboard from "./pages/Dashboard";
import Findings from "./pages/Findings";
import Login from "./pages/Login";
import Reports from "./pages/Reports";
import ScanDetailPage from "./pages/ScanDetailPage";
import Scans from "./pages/Scans";
import Targets from "./pages/Targets";

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="targets" element={<Targets />} />
          <Route path="scans" element={<Scans />} />
          <Route path="scans/:scanId" element={<ScanDetailPage />} />
          <Route path="findings" element={<Findings />} />
          <Route path="findings/:findingId" element={<Findings />} />
          <Route path="reports" element={<Reports />} />

          <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
            <Route path="audit-logs" element={<AuditLogs />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}