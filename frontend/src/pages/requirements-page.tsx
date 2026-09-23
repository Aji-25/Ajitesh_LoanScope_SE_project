import { ClipboardText, LockKey } from "@phosphor-icons/react";

import { Button } from "@/components/ui/button";

export function RequirementsPage() {
  return (
    <div>
      <p className="text-sm font-semibold text-[#d9ff76]">Requirement baseline</p>
      <h1 className="mt-3 text-4xl font-semibold">Requirements</h1>
      <p className="mt-4 max-w-2xl text-pretty text-base text-[#9b9b9b]">
        Review structured requirements, their sources, quality findings, and approval state.
      </p>
      <section className="mt-10 rounded-2xl border border-white/10 bg-[#181818] p-8 text-center sm:p-12">
        <span className="mx-auto grid size-12 place-items-center rounded-xl bg-[#272727] text-[#d9ff76]">
          <ClipboardText aria-hidden="true" size={24} />
        </span>
        <h2 className="mt-6 text-2xl font-semibold">No requirements yet</h2>
        <p className="mx-auto mt-3 max-w-lg text-pretty text-base text-[#9b9b9b]">
          Requirements will appear here after stakeholder input is captured and structured extraction is enabled.
        </p>
        <Button className="mt-8" disabled variant="secondary">
          <LockKey aria-hidden="true" /> Add requirement
        </Button>
      </section>
    </div>
  );
}
