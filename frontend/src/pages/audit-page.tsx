import {
  Archive,
  ChartBar,
  SpinnerGap,
  WarningCircle,
} from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { apiRequest } from "@/api/client";
import type { AuditEvent, Evaluation } from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

const metrics = [
  ["requirement_completeness", "Clear requirements", "Current requirements with no open wording issues."],
  ["evidence_grounding", "Policy evidence", "Current requirements linked to a policy passage by the AI review."],
  ["risk_coverage", "Risk review coverage", "Current requirement versions reviewed for risks. A review can find zero risks."],
  ["artifact_coverage", "Documents generated", "Distinct document types generated out of the nine available."],
] as const;

export function AuditPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    apiRequest<{ events: AuditEvent[]; evaluation: Evaluation | null }>(
      `/projects/${project.id}/audit`,
      { authenticated: true },
    )
      .then((data) => {
        setEvents(data.events);
        setEvaluation(data.evaluation);
      })
      .catch((reason: Error) => setError(reason.message));
  }, [project.id]);
  async function run() {
    setBusy(true);
    setError("");
    try {
      const latestEvaluation = await apiRequest<Evaluation>(
        `/projects/${project.id}/evaluations`,
        {
          method: "POST",
          authenticated: true,
        },
      );
      const audit = await apiRequest<{
        events: AuditEvent[];
        evaluation: Evaluation | null;
      }>(`/projects/${project.id}/audit`, { authenticated: true });
      setEvaluation(latestEvaluation);
      setEvents(audit.events);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Evaluation failed.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <div>
      <h1 className="text-4xl font-semibold">Audit and evaluation</h1>
      <p className="mt-4 max-w-2xl text-[#9b9b9b]">
        See what changed and when. Run an evaluation to save the current project counts and get an AI summary of what to do next.
      </p>
      <Button onClick={run} disabled={busy} className="mt-6">
        {busy ? <SpinnerGap aria-hidden="true" className="animate-spin" /> : <ChartBar aria-hidden="true" />}
        {busy ? "Reviewing snapshot…" : "Run evaluation"}
      </Button>
      {error && (
        <p role="alert" className="mt-5 flex gap-2 text-red-200">
          <WarningCircle />
          {error}
        </p>
      )}
      {evaluation && (
        <section className="mt-8 rounded-2xl border border-white/10 bg-[#181818] p-6">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-xl font-semibold">Latest quality snapshot</h2>
            <time className="text-sm text-[#bcbcbc]">{new Date(evaluation.created_at).toLocaleString()}</time>
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {metrics.map(([key, label, description]) => (
              <div key={key} className="rounded-xl bg-[#111] p-4">
                <p className="text-2xl font-semibold text-[#d9ff76]">{evaluation.metrics[key]}%</p>
                <p className="mt-1 text-sm font-semibold">{label}</p>
                <p className="mt-2 text-sm text-[#bcbcbc]">{description}</p>
              </div>
            ))}
          </div>
          <div className="mt-5 border-t border-white/10 pt-4">
            <h3 className="font-semibold">AI review</h3>
            <p className="mt-2 text-sm text-[#bcbcbc]">{evaluation.summary}</p>
            {!!evaluation.review_actions?.length && (
              <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-[#bcbcbc]">
                {evaluation.review_actions.map((action, index) => <li key={index}>{action}</li>)}
              </ul>
            )}
          </div>
        </section>
      )}
      <section className="mt-8">
        <h2 className="flex items-center gap-2 text-xl font-semibold">
          <Archive className="text-[#d9ff76]" />
          Audit timeline
        </h2>
        {events.length === 0 ? (
          <p className="mt-4 rounded-xl border border-dashed border-white/10 p-8 text-center text-[#888]">
            No audit events recorded yet.
          </p>
        ) : (
          <div className="mt-4 space-y-3">
            {events.map((event) => (
              <article
                key={event.id}
                className="rounded-xl border border-white/10 bg-[#181818] p-5"
              >
                <div className="flex flex-wrap justify-between gap-2">
                  <p className="font-medium">{event.action}</p>
                  <time className="text-xs text-[#aaa]">
                    {new Date(event.created_at).toLocaleString()}
                  </time>
                </div>
                <p className="mt-2 text-sm text-[#888]">
                  {event.agent_name === "live_ai" || (event.agent_name === "requirement_agent" && typeof event.event_metadata.provider_mode === "string" && event.event_metadata.provider_mode !== "mock")
                    ? "AI"
                    : event.actor_type === "user" || event.actor_type === "human"
                      ? "Project member"
                      : "Workspace"}
                </p>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
