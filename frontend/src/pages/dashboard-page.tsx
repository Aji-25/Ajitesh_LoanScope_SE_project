import { ArrowRight, FolderOpen, Plus } from "@phosphor-icons/react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiRequest } from "@/api/client";
import type { ProjectList } from "@/api/types";
import { Button } from "@/components/ui/button";
import { WorkspaceHeader } from "@/components/workspace-header";

export function DashboardPage() {
  const [projects, setProjects] = useState<ProjectList | null>(null);
  const [error, setError] = useState("");

  const loadProjects = useCallback(async () => {
    setError("");
    try {
      setProjects(await apiRequest<ProjectList>("/projects", { authenticated: true }));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Projects could not be loaded.");
    }
  }, []);

  useEffect(() => {
    void loadProjects();
  }, [loadProjects]);

  return (
    <div className="min-h-screen bg-[#131209]">
      <WorkspaceHeader />
      <main className="mx-auto max-w-7xl px-6 py-12">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold text-[#d9ff76]">Project workspace</p>
            <h1 className="mt-3 text-balance text-4xl font-semibold">Loan origination projects</h1>
            <p className="mt-3 max-w-2xl text-pretty text-base text-[#9b9b9b]">
              Continue stakeholder discovery or begin a new requirement baseline.
            </p>
          </div>
          <Button asChild>
            <Link to="/projects/new">
              <Plus aria-hidden="true" weight="bold" /> Create project
            </Link>
          </Button>
        </div>

        {error ? (
          <section className="mt-12 rounded-2xl border border-[#ff9b8f]/30 bg-[#181818] p-8 text-center">
            <h2 className="text-xl font-semibold">Projects are unavailable</h2>
            <p className="mt-3 text-sm text-[#ffb8af]">{error}</p>
            <Button className="mt-6" onClick={loadProjects} variant="secondary">Retry</Button>
          </section>
        ) : !projects ? (
          <div className="mt-12 grid gap-4 md:grid-cols-2" role="status">
            {[0, 1].map((item) => (
              <div className="h-56 animate-pulse rounded-2xl bg-[#181818]" key={item} />
            ))}
            <span className="sr-only">Loading projects</span>
          </div>
        ) : projects.total === 0 ? (
          <section className="mt-12 rounded-2xl border border-white/10 bg-[#181818] p-8 text-center sm:p-12">
            <span className="mx-auto grid size-12 place-items-center rounded-xl bg-[#272727] text-[#d9ff76]">
              <FolderOpen aria-hidden="true" size={24} />
            </span>
            <h2 className="mt-6 text-2xl font-semibold">Create your first project</h2>
            <p className="mx-auto mt-3 max-w-lg text-pretty text-base text-[#9b9b9b]">
              Start with the lending product, jurisdiction, project outcome, and primary stakeholder.
            </p>
            <Button asChild className="mt-8">
              <Link to="/projects/new">Create project</Link>
            </Button>
          </section>
        ) : (
          <section className="mt-12 grid gap-4 md:grid-cols-2" aria-label="Projects">
            {projects.items.map((project) => (
              <Link
                className="group rounded-2xl border border-white/10 bg-[#181818] p-6 transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] hover:-translate-y-1 hover:border-white/20 active:scale-[0.99]"
                key={project.id}
                to={`/projects/${project.id}/overview`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <span className="rounded-full bg-[#d9ff76]/10 px-3 py-1 text-xs font-semibold capitalize text-[#d9ff76]">
                      {project.current_stage}
                    </span>
                    <h2 className="mt-4 text-balance text-xl font-semibold">{project.name}</h2>
                  </div>
                  <ArrowRight className="text-[#6f6f6f] transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] group-hover:translate-x-1 group-hover:text-white" size={20} />
                </div>
                <p className="mt-4 line-clamp-3 text-pretty text-sm text-[#9b9b9b]">{project.summary}</p>
                <dl className="mt-8 grid grid-cols-2 gap-3">
                  {[
                    [project.stakeholder_count, "Stakeholders"],
                    [project.requirement_count, "Requirements"],
                  ].map(([value, label]) => (
                    <div className="rounded-lg bg-[#272727] p-3" key={label}>
                      <dd className="text-lg font-semibold">{value}</dd>
                      <dt className="text-xs text-[#8f8f8f]">{label}</dt>
                    </div>
                  ))}
                </dl>
              </Link>
            ))}
          </section>
        )}
      </main>
    </div>
  );
}
