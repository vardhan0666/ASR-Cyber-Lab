/**
 * Main ASR-Cyber-Lab application shell.
 *
 * Layers:
 * 0 = 3D cyber environment
 * 2 = application content
 * 4/5 = header and sidebar
 */

import { Outlet } from "react-router-dom";

import Header from "./Header";
import Sidebar from "./Sidebar";
import PageTransition from "../common/PageTransition";
import CyberScene from "../common/CyberScene";

export default function Layout() {
  return (
    <div className="asr-shell relative flex h-full min-h-screen">
      {/* 3D WebGL environment */}
      <CyberScene />

      {/* Application interface */}
      <div className="relative z-[2] flex min-w-0 flex-1 flex-col overflow-hidden">
        <Header />

        <main className="asr-main flex-1 p-4 sm:p-5 lg:p-6">
          <PageTransition>
            <Outlet />
          </PageTransition>
        </main>
      </div>

      {/* Sidebar */}
      <div className="relative z-[5]">
        <Sidebar />
      </div>
    </div>
  );
}