import {
  Archive,
  ChartBar,
  ChatCircleDots,
  CheckSquare,
  ClipboardText,
  FileText,
  Gavel,
  House,
  ShieldCheck,
  Siren,
} from "@phosphor-icons/react";
import { useCallback, useEffect, useState } from "react";
import { Link, NavLink, Outlet, useParams } from "react-router-dom";

import { apiRequest } from "@/api/client";
import type { Project } from "@/api/types";
import { WorkspaceHeader } from "@/components/workspace-header";
import { cn } from "@/lib/utils";

const navigation = [
  ["overview", "Overview", House],
  ["interview", "Interview", ChatCircleDots],
  ["requirements", "Requirements", ClipboardText],
  ["compliance", "Compliance", Gavel],
  ["security", "Security", ShieldCheck],
  ["risks", "Risks", Siren],
  ["sdlc", "SDLC", ChartBar],
  ["approvals", "Approvals", CheckSquare],
  ["documents", "Documents", FileText],
  ["audit", "Audit", Archive],
] as const;

export type ProjectOutletContext = { project: Project; reload: () => Promise<void> };

export function ProjectLayout() {
  const { projectId } = useParams();
  const [project, setProject] = useState<Project | null>(null);
  const [error, setError] = useState("");

  const loadProject = useCallback(async () => {
    if (!projectId) return;
    setError("");
    try {
      setProject(await apiRequest<Project>(`/projects/${projectId}`, { authenticated: true }));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Project could not be loaded.");
    }
  }, [projectId]);

  useEffect(() => {
    void loadProject();
  }, [loadProject]);

  if (error) {
    return (
      <div className="min-h-screen bg-[#131209]">
        <WorkspaceHeader />
        <main className="mx-auto max-w-xl px-6 py-24 text-center">
          <h1 className="text-3xl font-semibold">Project unavailable</h1>
          <p className="mt-4 text-pretty text-base text-[#9b9b9b]">{error}</p>
          <Link className="mt-8 inline-block rounded-lg text-sm font-semibold text-[#d9ff76]" to="/dashboard">
            Return to dashboard
          </Link>
        </main>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-[#131209]">
        <WorkspaceHeader />
        <main className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[240px_1fr]" role="status">
          <div className="h-96 animate-pulse rounded-2xl bg-[#181818]" />
          <div className="space-y-4">
            <div className="h-10 w-1/2 animate-pulse rounded-lg bg-[#272727]" />
            <div className="h-64 animate-pulse rounded-2xl bg-[#181818]" />
          </div>
          <span className="sr-only">Loading project workspace</span>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#131209]">
      <WorkspaceHeader />
      <div className="mx-auto grid min-w-0 max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[240px_minmax(0,1fr)] lg:py-8">
        <aside className="min-w-0 lg:sticky lg:top-8 lg:self-start">
          <div className="min-w-0 overflow-hidden rounded-2xl border border-white/10 bg-[#181818] p-3">
            <div className="px-3 py-3">
              <Link className="text-xs font-semibold text-[#9b9b9b] hover:text-white" to="/dashboard">
                All projects
              </Link>
              <h2 className="mt-2 text-pretty text-base font-semibold">{project.name}</h2>
              <span className="mt-3 inline-flex rounded-full bg-[#d9ff76]/10 px-3 py-1 text-xs font-semibold capitalize text-[#d9ff76]">
                {project.current_stage}
              </span>
            </div>
            <nav aria-label="Project navigation" className="mt-2 flex max-w-full gap-2 overflow-x-auto lg:flex-col">
              {navigation.map(([path, label, Icon]) => (
                <NavLink
                  className={({ isActive }) =>
                    cn(
                      "flex shrink-0 items-center gap-3 rounded-lg px-3 py-2 text-sm font-semibold transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] active:scale-[0.98]",
                      isActive
                        ? "bg-[#d9ff76] text-[#131209]"
                        : "text-[#9b9b9b] hover:bg-[#272727] hover:text-white",
                    )
                  }
                  key={path}
                  to={`/projects/${project.id}/${path}`}
                >
                  <Icon aria-hidden="true" size={18} /> {label}
                </NavLink>
              ))}
            </nav>
          </div>
        </aside>
        <main className="min-w-0" id="main-content">
          <Outlet context={{ project, reload: loadProject } satisfies ProjectOutletContext} />
        </main>
      </div>
    </div>
  );
}
