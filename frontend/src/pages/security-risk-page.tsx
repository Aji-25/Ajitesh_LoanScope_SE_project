import { ShieldCheck, SpinnerGap, WarningCircle } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { apiRequest } from "@/api/client";
import type { Risk, SecurityFinding } from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

type Data = { findings: SecurityFinding[]; risks: Risk[] };
export function SecurityRiskPage({ view }: { view: "security" | "risks" }) {
  const { project } = useOutletContext<ProjectOutletContext>();
  const [data, setData] = useState<Data | null>(null); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  useEffect(() => { apiRequest<Data>(`/projects/${project.id}/security-risk`, { authenticated: true }).then(setData).catch((reason: Error) => setError(reason.message)); }, [project.id]);
  async function generate() { setBusy(true); setError(""); try { setData(await apiRequest<Data>(`/projects/${project.id}/security-risk/generate`, { method: "POST", authenticated: true })); } catch (reason) { setError(reason instanceof Error ? reason.message : "Analysis failed."); } finally { setBusy(false); } }
  const title = view === "security" ? "Security review" : "Risk register"; const items = view === "security" ? data?.findings : data?.risks;
  return <div><p className="text-sm font-semibold text-[#d9ff76]">{view === "security" ? "Threat and control analysis" : "Prioritized exposure"}</p><h1 className="mt-3 text-4xl font-semibold">{title}</h1><p className="mt-4 max-w-2xl text-[#9b9b9b]">Review findings derived from project requirements with linked mitigations and accountable owners.</p><Button onClick={generate} disabled={busy} className="mt-6">{busy ? <SpinnerGap className="animate-spin" /> : <ShieldCheck />}Generate analysis</Button>{error && <p role="alert" className="mt-5 flex gap-2 text-red-200"><WarningCircle />{error}</p>}{!data ? <p className="mt-8 text-[#888]">Loading analysis…</p> : items?.length === 0 ? <p className="mt-8 rounded-xl border border-dashed border-white/10 p-8 text-center text-[#888]">No findings yet. Generate analysis after capturing requirements.</p> : <div className="mt-8 space-y-4">{view === "security" ? data.findings.map((item) => <article key={item.id} className="rounded-2xl border border-white/10 bg-[#181818] p-6"><div className="flex justify-between gap-4"><h2 className="text-lg font-semibold">{item.title}</h2><span className="text-xs font-semibold uppercase text-amber-200">{item.severity}</span></div><p className="mt-3 text-sm text-[#aaa]">{item.description}</p><p className="mt-4 rounded-lg bg-[#111] p-3 text-sm text-[#d9ff76]">{item.recommendation}</p></article>) : data.risks.map((item) => <article key={item.id} className="rounded-2xl border border-white/10 bg-[#181818] p-6"><div className="flex justify-between gap-4"><h2 className="font-mono text-[#d9ff76]">{item.risk_code}</h2><span className="rounded-full bg-amber-300/10 px-3 py-1 text-sm text-amber-200">Score {item.score}/25</span></div><p className="mt-3">{item.description}</p><p className="mt-3 text-sm text-[#888]">Likelihood {item.likelihood}/5 · Impact {item.impact}/5 · Owner: {item.owner_role}</p><p className="mt-4 rounded-lg bg-[#111] p-3 text-sm text-[#bbb]">Mitigation: {item.mitigation}</p></article>)}</div>}</div>;
}
