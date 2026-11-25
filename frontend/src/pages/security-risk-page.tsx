import { CaretDown, ShieldCheck, SpinnerGap, WarningCircle } from "@phosphor-icons/react";
import { useEffect, useRef, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { apiRequest } from "@/api/client";
import type { RequirementList, Risk, SecurityFinding } from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

type Analysis = { findings: SecurityFinding[]; risks: Risk[] };

export function SecurityRiskPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [requirementCodes, setRequirementCodes] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [checked, setChecked] = useState(false);
  const initialLoad = useRef<AbortController | null>(null);
  const path = `/projects/${project.id}`;

  useEffect(() => {
    const results = new AbortController();
    const labels = new AbortController();
    initialLoad.current = results;
    setAnalysis(null);
    setChecked(false);
    setError("");
    setRequirementCodes({});
    apiRequest<Analysis>(`${path}/security-risk`, { authenticated: true, signal: results.signal })
      .then((data) => {
        if (!results.signal.aborted) setAnalysis(data);
      })
      .catch((reason: Error) => {
        if (!results.signal.aborted) setError(reason.message);
      });
    apiRequest<RequirementList>(`${path}/requirements`, { authenticated: true, signal: labels.signal })
      .then(({ items }) => setRequirementCodes(Object.fromEntries(items.map(({ id, requirement_code }) => [id, requirement_code]))))
      .catch(() => { /* Risk results can still be shown without the requirement labels. */ });
    return () => {
      results.abort();
      labels.abort();
    };
  }, [path]);

  async function generate() {
    initialLoad.current?.abort();
    setBusy(true);
    setError("");
    try {
      setAnalysis(await apiRequest<Analysis>(`${path}/security-risk/generate`, {
        method: "POST",
        authenticated: true,
      }));
      setChecked(true);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not check risks.");
    } finally {
      setBusy(false);
    }
  }

  const findings = new Map(analysis?.findings.map((finding) => [
    `${finding.requirement_id}/${finding.category}`, finding,
  ]));
  const risks = [...(analysis?.risks ?? [])].sort((left, right) => right.score - left.score);

  return (
    <div>
      <h1 className="text-4xl font-semibold">Security &amp; risks</h1>
      <p className="mt-4 max-w-2xl text-[#9b9b9b]">
        AI reviews the controls already in your requirements and looks for risks that could remain if those controls are put in place.
      </p>
      <Button onClick={() => void generate()} disabled={busy} className="mt-6">
        {busy ? <SpinnerGap aria-hidden="true" className="animate-spin" /> : <ShieldCheck aria-hidden="true" />}
        {busy ? "Reviewing requirements…" : "Check risks with AI"}
      </Button>
      {error && <p role="alert" className="mt-5 flex gap-2 text-red-200"><WarningCircle aria-hidden="true" />{error}</p>}
      {checked && !busy && !error && (
        <p role="status" className="mt-4 text-sm text-[#bcbcbc]">
          {risks.length === 0
            ? "Check complete. The AI review found no specific remaining risks in the current requirements."
            : `Check complete. Found ${risks.length} ${risks.length === 1 ? "risk" : "risks"}.`}
        </p>
      )}
      {!busy && !checked && !error && risks.length === 0 && (
        <p role="status" className="mt-8 rounded-xl border border-dashed border-white/10 p-6 text-[#9b9b9b]">
          {analysis ? "Run an AI risk review to see whether anything still needs attention." : "Loading saved results…"}
        </p>
      )}
      <div className="mt-8 space-y-4">
        {risks.map((risk) => {
          const finding = findings.get(`${risk.requirement_id}/${risk.category}`);
          const requirement = risk.requirement_id ? requirementCodes[risk.requirement_id] : undefined;
          return (
            <details key={risk.id} className="group rounded-2xl border border-white/10 bg-[#181818]">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 p-5 focus-visible:outline-2 focus-visible:outline-[#d9ff76] [&::-webkit-details-marker]:hidden">
                <div>
                  <span className="text-lg font-semibold">{finding?.title ?? risk.category.replaceAll("_", " ")}</span>
                  <p className="mt-1 text-sm text-[#9b9b9b]">{risk.risk_code}{requirement && ` · ${requirement}`}</p>
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <span className="rounded-full bg-amber-300/10 px-3 py-1 text-sm capitalize text-amber-200">
                    {finding?.severity && `${finding.severity} · `}{risk.score}/25
                  </span>
                  <CaretDown aria-hidden="true" className="group-open:rotate-180" />
                </div>
              </summary>
              <div className="space-y-4 border-t border-white/10 px-5 py-4 text-sm">
                <div>
                  <h2 className="font-semibold">What your requirement already covers</h2>
                  <p className="mt-1 text-[#bcbcbc]">{risk.existing_control}</p>
                </div>
                <div>
                  <h2 className="font-semibold">What could still go wrong</h2>
                  <p className="mt-1 text-[#bcbcbc]">{risk.description}</p>
                </div>
                <div>
                  <h2 className="font-semibold">How the score was calculated</h2>
                  <p className="mt-1 text-[#bcbcbc]">Likelihood {risk.likelihood}/5 × impact {risk.impact}/5 = {risk.score}/25. AI estimated likelihood and impact assuming the stated control is implemented.</p>
                  <p className="mt-2 whitespace-pre-line text-[#bcbcbc]">{risk.rating_reason}</p>
                </div>
                <div>
                  <h2 className="font-semibold text-[#d9ff76]">What to add or test</h2>
                  <p className="mt-1 text-[#bcbcbc]">{risk.mitigation}</p>
                  <p className="mt-2 text-[#9b9b9b]">Suggested owner: {risk.owner_role}</p>
                </div>
              </div>
            </details>
          );
        })}
      </div>
    </div>
  );
}
