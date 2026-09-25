import type { ReactNode } from "react";
import { useLocation } from "react-router-dom";

interface PageTransitionProps {
  children: ReactNode;
}

export default function PageTransition({
  children,
}: PageTransitionProps) {
  const location = useLocation();

  return (
    <div
      key={location.pathname}
      className="asr-page-enter"
    >
      {children}
    </div>
  );
}