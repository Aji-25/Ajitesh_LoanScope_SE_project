import { ArrowRight, ChatCircleDots, CheckCircle, ClipboardText, Users } from "@phosphor-icons/react";
import { Link, useOutletContext } from "react-router-dom";

import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

export function ProjectOverviewPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const summaryCards = [
    { icon: Users, value: project.stakeholder_count, label: "Stakeholders" },
    { icon: ClipboardText, value: project.requirement_count, label: "Requirements" },
    { icon: CheckCircle, value: project.pending_approval_count, label: "Pending approvals" },
  ];

  return (
    <div>
      <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold capitalize text-[#d9ff76]">{project.current_stage} stage</p>
          <h1 className="mt-3 text-balance text-4xl font-semibold">{project.name}</h1>
          <p className="mt-4 max-w-3xl text-pretty text-base text-[#9b9b9b]">{project.summary}</p>
        </div>
        <Button asChild>
          <Link to={`/projects/${project.id}/interview`}>
            Continue discovery <ArrowRight aria-hidden="true" />
          </Link>
        </Button>
      </div>

      <section className="mt-10 grid gap-4 sm:grid-cols-3" aria-label="Project summary">
        {summaryCards.map(({ icon: Icon, value, label }) => (
          <article className="rounded-2xl border border-white/10 bg-[#181818] p-6" key={label}>
            <Icon aria-hidden="true" className="text-[#d9ff76]" size={22} />
            <p className="mt-6 text-3xl font-semibold">{value}</p>
            <p className="mt-1 text-sm text-[#8f8f8f]">{label}</p>
          </article>
        ))}
      </section>

      <section className="mt-6 rounded-2xl border border-white/10 bg-[#181818] p-6 sm:p-8">
        <div className="flex items-start gap-4">
          <span className="grid size-12 shrink-0 place-items-center rounded-xl bg-[#272727] text-[#d9ff76]">
            <ChatCircleDots aria-hidden="true" size={24} />
          </span>
          <div>
            <p className="text-sm font-semibold text-[#d9ff76]">Next action</p>
            <h2 className="mt-2 text-2xl font-semibold">Prepare the first stakeholder interview.</h2>
            <p className="mt-3 max-w-2xl text-pretty text-base text-[#9b9b9b]">
              Confirm the project context and identify the first unanswered business outcome before requirement extraction begins.
            </p>
            <Button asChild className="mt-6" variant="secondary">
              <Link to={`/projects/${project.id}/interview`}>Open interview workspace</Link>
            </Button>
          </div>
        </div>
      </section>

      <section className="mt-6 grid gap-4 md:grid-cols-2">
        <article className="rounded-2xl border border-white/10 bg-[#181818] p-6">
          <h2 className="text-lg font-semibold">Project details</h2>
          <dl className="mt-6 space-y-4 text-sm">
            <div><dt className="text-[#8f8f8f]">Product</dt><dd className="mt-1">{project.product_type}</dd></div>
            <div><dt className="text-[#8f8f8f]">Jurisdiction</dt><dd className="mt-1">{project.jurisdiction}</dd></div>
            <div><dt className="text-[#8f8f8f]">Status</dt><dd className="mt-1 capitalize">{project.status}</dd></div>
          </dl>
        </article>
        <article className="rounded-2xl border border-white/10 bg-[#181818] p-6">
          <h2 className="text-lg font-semibold">Recent activity</h2>
          <div className="mt-6 rounded-xl bg-[#272727] p-4">
            <p className="text-sm font-semibold">Project created</p>
            <p className="mt-2 text-sm text-[#8f8f8f]">Discovery is ready to begin. Later actions will appear here as the workflow advances.</p>
          </div>
        </article>
      </section>
    </div>
  );
}
