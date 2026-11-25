import { ChatCircleDots, SpinnerGap, WarningCircle } from "@phosphor-icons/react";
import { FormEvent, useState } from "react";
import { useOutletContext } from "react-router-dom";

import { apiRequest } from "@/api/client";
import type { RequirementExtraction } from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

export function InterviewPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const [source, setSource] = useState("Loan Operations Manager");
  const [statement, setStatement] = useState("");
  const [result, setResult] = useState<RequirementExtraction | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const extracted = await apiRequest<RequirementExtraction>(`/projects/${project.id}/messages`, {
        method: "POST",
        authenticated: true,
        body: JSON.stringify({
          project_id: project.id,
          stakeholder_text: statement,
          source_stakeholder: source,
          accept_candidates: true,
        }),
      });
      setResult(extracted);
      setStatement("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Extraction failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <p className="text-sm font-semibold text-[#d9ff76]">Guided discovery</p>
      <h1 className="mt-3 text-4xl font-semibold">Stakeholder interview</h1>
      <p className="mt-4 max-w-2xl text-pretty text-base text-[#9b9b9b]">Capture source statements and turn them into reviewable, traceable requirements for {project.name}.</p>
      <div className="mt-10 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <form onSubmit={submit} className="rounded-2xl border border-white/10 bg-[#181818] p-6">
          <label className="text-sm font-medium" htmlFor="source">Stakeholder or source</label>
          <input id="source" required minLength={2} value={source} onChange={(event) => setSource(event.target.value)} className="mt-2 h-12 w-full rounded-xl border border-white/10 bg-[#111] px-4 outline-none transition focus:border-[#d9ff76] focus:ring-2 focus:ring-[#d9ff76]/20" />
          <label className="mt-6 block text-sm font-medium" htmlFor="statement">Stakeholder statement</label>
          <textarea id="statement" required minLength={10} maxLength={5000} rows={8} value={statement} onChange={(event) => setStatement(event.target.value)} placeholder="Applicants must be able to upload income evidence and receive a validation result within 30 seconds." className="mt-2 w-full resize-y rounded-xl border border-white/10 bg-[#111] p-4 outline-none transition placeholder:text-[#666] focus:border-[#d9ff76] focus:ring-2 focus:ring-[#d9ff76]/20" />
          {error && <p role="alert" className="mt-4 flex gap-2 text-sm text-red-300"><WarningCircle size={18} />{error}</p>}
          <Button className="mt-6 w-full" disabled={loading || statement.trim().length < 10}>{loading ? <SpinnerGap className="animate-spin" /> : <ChatCircleDots />} {loading ? "Extracting…" : "Extract requirements"}</Button>
        </form>
        <section aria-live="polite" className="rounded-2xl border border-white/10 bg-[#181818] p-6">
          <h2 className="text-xl font-semibold">Structured output</h2>
          {!result ? <p className="mt-4 text-[#9b9b9b]">Submit a stakeholder statement to see typed requirement candidates and uncertainty.</p> : <div className="mt-5 space-y-4">
            <p className="text-sm text-[#9b9b9b]">{result.extraction.summary}</p>
            {result.extraction.candidates.map((candidate, index) => <article key={`${candidate.statement}-${index}`} className="rounded-xl border border-white/10 bg-[#111] p-5">
              <div className="flex flex-wrap gap-2">{candidate.categories.map((category) => <span key={category} className="rounded-full bg-[#d9ff76]/10 px-2.5 py-1 text-xs text-[#d9ff76]">{category}</span>)}</div>
              <p className="mt-4 font-medium">{candidate.statement}</p>
              <p className="mt-3 text-sm text-[#9b9b9b]">
                Source: {result.persisted_requirements[index]?.source_stakeholder ?? candidate.source}
              </p>
              {candidate.clarification_needed && <p className="mt-3 rounded-lg bg-amber-300/10 p-3 text-sm text-amber-200">Clarification needed: {candidate.uncertainty_reason}</p>}
            </article>)}
          </div>}
        </section>
      </div>
    </div>
  );
}
