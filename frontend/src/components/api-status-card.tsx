import { CheckCircle, CloudCheck, WarningCircle } from "@phosphor-icons/react";
import { useState } from "react";

import { Button } from "@/components/ui/button";

type Status = "idle" | "loading" | "connected" | "error";

export function ApiStatusCard() {
  const [status, setStatus] = useState<Status>("idle");
  const actionLabel = status === "loading" ? "Checking" : status === "error" ? "Retry" : "Check";

  async function checkConnection() {
    setStatus("loading");
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL ?? "http://localhost:8000"}/health`);
      if (!response.ok) throw new Error("Service unavailable");
      setStatus("connected");
    } catch {
      setStatus("error");
    }
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-[#181818] p-4">
      <div className="flex items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <span className="grid size-10 shrink-0 place-items-center rounded-lg bg-[#272727] text-[#d9ff76]">
            <CloudCheck aria-hidden="true" size={22} />
          </span>
          <div>
            <p className="text-sm font-semibold text-white">Workspace service</p>
            <p className="text-pretty text-sm text-[#9b9b9b]">
              {status === "idle" && "Ready for a connection check"}
              {status === "loading" && "Checking database readiness"}
              {status === "connected" && "API and database are connected"}
              {status === "error" && "Connection failed. Start the local stack and try again."}
            </p>
          </div>
        </div>
        {status === "connected" ? (
          <CheckCircle aria-label="Connected" className="shrink-0 text-[#d9ff76]" size={24} weight="fill" />
        ) : status === "error" ? (
          <WarningCircle aria-label="Connection error" className="shrink-0 text-[#ff9b8f]" size={24} weight="fill" />
        ) : (
          <Button disabled={status === "loading"} onClick={checkConnection} size="small" variant="secondary">
            {actionLabel}
          </Button>
        )}
      </div>
      {status === "loading" && (
        <div className="mt-4 h-2 overflow-hidden rounded-full bg-[#272727]" role="status">
          <div className="h-full w-2/3 animate-pulse rounded-full bg-[#d9ff76]" />
          <span className="sr-only">Checking service readiness</span>
        </div>
      )}
    </div>
  );
}
