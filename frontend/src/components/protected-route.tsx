import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "@/contexts/auth-store";

export function ProtectedRoute() {
  const { loading, user } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <main className="grid min-h-screen place-items-center bg-[#131209] px-6" role="status">
        <div className="w-full max-w-sm space-y-4">
          <div className="h-10 w-2/3 animate-pulse rounded-lg bg-[#272727]" />
          <div className="h-24 animate-pulse rounded-xl bg-[#1f1f1f]" />
          <span className="sr-only">Restoring your workspace</span>
        </div>
      </main>
    );
  }

  if (!user) return <Navigate replace state={{ from: location }} to="/login" />;
  return <Outlet />;
}
