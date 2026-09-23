import { LockKey } from "@phosphor-icons/react";

import { Button } from "@/components/ui/button";

type ProjectStagePageProps = {
  eyebrow: string;
  title: string;
  description: string;
};

export function ProjectStagePage({ eyebrow, title, description }: ProjectStagePageProps) {
  return (
    <div>
      <p className="text-sm font-semibold text-[#d9ff76]">{eyebrow}</p>
      <h1 className="mt-3 text-4xl font-semibold">{title}</h1>
      <p className="mt-4 max-w-2xl text-pretty text-base text-[#9b9b9b]">{description}</p>
      <section className="mt-10 rounded-2xl border border-white/10 bg-[#181818] p-8 text-center sm:p-12">
        <span className="mx-auto grid size-12 place-items-center rounded-xl bg-[#272727] text-[#d9ff76]">
          <LockKey aria-hidden="true" size={24} />
        </span>
        <h2 className="mt-6 text-2xl font-semibold">This stage is not active yet</h2>
        <p className="mx-auto mt-3 max-w-lg text-pretty text-base text-[#9b9b9b]">
          Complete the earlier workflow stages before this project record becomes available.
        </p>
        <Button className="mt-8" disabled variant="secondary">Stage locked</Button>
      </section>
    </div>
  );
}
