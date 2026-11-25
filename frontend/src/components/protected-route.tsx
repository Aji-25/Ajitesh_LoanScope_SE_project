import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "@/contexts/auth-store";

export function ProtectedRoute() {
  const { loading, retrySession, sessionError, user } = useAuth();
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

  if (sessionError) {
    return (
      <main className="grid min-h-screen place-items-center bg-[#131209] px-6">
        <section className="w-full max-w-md rounded-2xl border border-red-200/20 bg-[#181818] p-8 text-center">
          <h1 className="text-2xl font-semibold">Workspace temporarily unavailable</h1>
          <p role="alert" className="mt-4 text-red-100">
            {sessionError}
          </p>
          <button
            type="button"
            onClick={retrySession}
            className="mt-6 rounded-lg bg-[#d9ff76] px-5 py-3 font-semibold text-[#131209] outline-none transition hover:bg-[#e4ff9e] focus-visible:ring-2 focus-visible:ring-[#d9ff76] focus-visible:ring-offset-2 focus-visible:ring-offset-[#131209] active:scale-[0.98]"
          >
            Retry connection
          </button>
        </section>
      </main>
    );
  }

  if (!user) return <Navigate replace state={{ from: location }} to="/login" />;
  return <Outlet />;
}
