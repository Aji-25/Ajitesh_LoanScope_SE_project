import { ChatCircleDots, LockKey } from "@phosphor-icons/react";
import { useOutletContext } from "react-router-dom";

import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

export function InterviewPage() {
  const { project } = useOutletContext<ProjectOutletContext>();

  return (
    <div>
      <p className="text-sm font-semibold text-[#d9ff76]">Guided discovery</p>
      <h1 className="mt-3 text-4xl font-semibold">Stakeholder interview</h1>
      <p className="mt-4 max-w-2xl text-pretty text-base text-[#9b9b9b]">
        The interview workspace will ask focused questions and preserve the source of every answer for {project.name}.
      </p>
      <section className="mt-10 rounded-2xl border border-white/10 bg-[#181818] p-8 text-center sm:p-12">
        <span className="mx-auto grid size-12 place-items-center rounded-xl bg-[#272727] text-[#d9ff76]">
          <ChatCircleDots aria-hidden="true" size={24} />
        </span>
        <h2 className="mt-6 text-2xl font-semibold">No interview has started</h2>
        <p className="mx-auto mt-3 max-w-lg text-pretty text-base text-[#9b9b9b]">
          The adaptive interview agent is introduced in a later phase. This workspace is ready for that workflow without simulating responses.
        </p>
        <Button className="mt-8" disabled>
          <LockKey aria-hidden="true" /> Start interview
        </Button>
      </section>
    </div>
  );
}
