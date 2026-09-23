import { CheckSquare, LockKey } from "@phosphor-icons/react";

import { Button } from "@/components/ui/button";

export function ApprovalsPage() {
  return (
    <div>
      <p className="text-sm font-semibold text-[#d9ff76]">Human review</p>
      <h1 className="mt-3 text-4xl font-semibold">Approvals</h1>
      <p className="mt-4 max-w-2xl text-pretty text-base text-[#9b9b9b]">
        High impact requirements, compliance interpretations, and delivery recommendations will wait here for accountable review.
      </p>
      <section className="mt-10 rounded-2xl border border-white/10 bg-[#181818] p-8 text-center sm:p-12">
        <span className="mx-auto grid size-12 place-items-center rounded-xl bg-[#272727] text-[#d9ff76]">
          <CheckSquare aria-hidden="true" size={24} />
        </span>
        <h2 className="mt-6 text-2xl font-semibold">No decisions are waiting</h2>
        <p className="mx-auto mt-3 max-w-lg text-pretty text-base text-[#9b9b9b]">
          Approval requests will be created only when a workflow reaches a real human review point.
        </p>
        <Button className="mt-8" disabled variant="secondary">
          <LockKey aria-hidden="true" /> Review selection
        </Button>
      </section>
    </div>
  );
}
