import { ClipboardText, SpinnerGap, WarningCircle } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";

import { apiRequest } from "@/api/client";
import type { RequirementList } from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

export function RequirementsPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const [data, setData] = useState<RequirementList | null>(null);
  const [error, setError] = useState("");
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    apiRequest<RequirementList>(`/projects/${project.id}/requirements`, { authenticated: true }).then(setData).catch((requestError: Error) => setError(requestError.message));
  }, [project.id]);

  async function analyze() {
    setAnalyzing(true);
    setError("");
    try {
      const result = await apiRequest<RequirementList & { ambiguity_count: number; conflict_count: number }>(`/projects/${project.id}/requirements/analyze`, { method: "POST", authenticated: true });
      setData({ items: result.items, total: result.items.length });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Analysis failed.");
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div>
      <p className="text-sm font-semibold text-[#d9ff76]">Requirement baseline</p>
      <h1 className="mt-3 text-4xl font-semibold">Requirements</h1>
      <p className="mt-4 max-w-2xl text-pretty text-base text-[#9b9b9b]">Review structured requirements, their sources, quality findings, and approval state.</p>
      {data && data.total > 0 && <Button onClick={analyze} disabled={analyzing} variant="secondary" className="mt-6">{analyzing ? <SpinnerGap className="animate-spin" /> : <ClipboardText />} {analyzing ? "Analyzing…" : "Analyze quality"}</Button>}
      {error ? <div role="alert" className="mt-10 flex gap-3 rounded-xl border border-red-300/20 bg-red-300/10 p-5 text-red-200"><WarningCircle size={22} />{error}</div> : !data ? <div className="mt-10 flex items-center gap-3 text-[#9b9b9b]"><SpinnerGap className="animate-spin" />Loading requirements…</div> : data.total === 0 ? <section className="mt-10 rounded-2xl border border-white/10 bg-[#181818] p-8 text-center sm:p-12">
        <ClipboardText className="mx-auto text-[#d9ff76]" size={42} /><h2 className="mt-6 text-2xl font-semibold">No requirements yet</h2><p className="mx-auto mt-3 max-w-lg text-[#9b9b9b]">Capture a stakeholder statement to create the first traceable requirement.</p><Button asChild className="mt-8"><Link to={`/projects/${project.id}/interview`}>Start discovery</Link></Button>
      </section> : <div className="mt-10 space-y-4">{data.items.map((item) => <article key={item.id} className="rounded-2xl border border-white/10 bg-[#181818] p-6 transition hover:border-white/20">
        <div className="flex flex-wrap items-center justify-between gap-3"><span className="font-mono text-sm text-[#d9ff76]">{item.requirement_code}</span><span className="rounded-full bg-white/5 px-3 py-1 text-xs capitalize text-[#bcbcbc]">{item.approval_status}</span></div>
        <h2 className="mt-4 text-lg font-medium">{item.statement}</h2><div className="mt-4 flex flex-wrap gap-2">{item.categories.map((category) => <span key={category} className="rounded-full bg-[#272727] px-2.5 py-1 text-xs text-[#bcbcbc]">{category}</span>)}</div><p className="mt-4 text-sm text-[#888]">Source: {item.source_stakeholder} · Confidence {Math.round(item.confidence * 100)}% · Version {item.version}</p>
        {item.quality_findings.length > 0 && <div className="mt-4 space-y-2">{item.quality_findings.map((finding, index) => <div key={`${finding.kind}-${index}`} className="rounded-lg border border-amber-200/10 bg-amber-200/5 p-3 text-sm"><p className="font-medium capitalize text-amber-200">{finding.kind}</p><p className="mt-1 text-[#bcbcbc]">{finding.message}</p><p className="mt-1 text-[#888]">{finding.question}</p></div>)}</div>}
      </article>)}</div>}
    </div>
  );
}
