import {
  ArrowsClockwise,
  CheckCircle,
  ClipboardText,
  PencilSimple,
  SpinnerGap,
  WarningCircle,
} from "@phosphor-icons/react";
import { type FormEvent, useEffect, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";

import { apiRequest } from "@/api/client";
import type {
  Requirement,
  RequirementList,
  RequirementWorkflow,
} from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

export function RequirementsPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const [data, setData] = useState<RequirementList | null>(null);
  const [error, setError] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisSummary, setAnalysisSummary] = useState<{
    requirements: number;
    ambiguities: number;
    conflicts: number;
  } | null>(null);
  const [editing, setEditing] = useState<string | null>(null);
  const [clarification, setClarification] = useState("");
  const [criterion, setCriterion] = useState("");
  const [saving, setSaving] = useState(false);
  const [workflow, setWorkflow] = useState<RequirementWorkflow | null>(null);
  const [workflowBusy, setWorkflowBusy] = useState(false);
  const [workflowClarifications, setWorkflowClarifications] = useState<
    string[]
  >([]);

  useEffect(() => {
    apiRequest<RequirementList>(`/projects/${project.id}/requirements`, {
      authenticated: true,
    })
      .then(setData)
      .catch((requestError: Error) => setError(requestError.message));
    apiRequest<RequirementWorkflow | null>(
      `/projects/${project.id}/workflows/latest`,
      { authenticated: true },
    )
      .then((latest) => {
        if (!latest) return;
        setWorkflow(latest);
        setWorkflowClarifications(latest.state.statements ?? []);
      })
      .catch((requestError: Error) => setError(requestError.message));
  }, [project.id]);

  async function analyze() {
    setAnalyzing(true);
    setError("");
    setAnalysisSummary(null);
    try {
      const result = await apiRequest<
        RequirementList & { ambiguity_count: number; conflict_count: number }
      >(`/projects/${project.id}/requirements/analyze`, {
        method: "POST",
        authenticated: true,
      });
      setData({ items: result.items, total: result.items.length });
      setAnalysisSummary({
        requirements: result.items.length,
        ambiguities: result.ambiguity_count,
        conflicts: result.conflict_count,
      });
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Analysis failed.",
      );
    } finally {
      setAnalyzing(false);
    }
  }

  async function startWorkflow() {
    setWorkflowBusy(true);
    setError("");
    try {
      const started = await apiRequest<RequirementWorkflow>(
        `/projects/${project.id}/workflows`,
        {
          method: "POST",
          authenticated: true,
          body: JSON.stringify({ max_iterations: 2 }),
        },
      );
      setWorkflow(started);
      setWorkflowClarifications(started.state.statements ?? []);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Workflow failed.",
      );
    } finally {
      setWorkflowBusy(false);
    }
  }

  async function resumeWorkflow(event: FormEvent) {
    event.preventDefault();
    if (!workflow) return;
    setWorkflowBusy(true);
    setError("");
    try {
      const resumed = await apiRequest<RequirementWorkflow>(
        `/workflows/${workflow.id}/resume`,
        {
          method: "POST",
          authenticated: true,
          body: JSON.stringify({ clarifications: workflowClarifications }),
        },
      );
      setWorkflow(resumed);
      setWorkflowClarifications(resumed.state.statements ?? []);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Workflow resume failed.",
      );
    } finally {
      setWorkflowBusy(false);
    }
  }

  function beginClarification(item: Requirement) {
    setEditing(item.id);
    setClarification(item.statement);
    setCriterion(item.acceptance_criteria[0] ?? "");
    setError("");
  }

  async function saveClarification(event: FormEvent, item: Requirement) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const updated = await apiRequest<Requirement>(
        `/projects/${project.id}/requirements/${item.id}`,
        {
          method: "PATCH",
          authenticated: true,
          body: JSON.stringify({
            statement: clarification,
            acceptance_criteria: [criterion],
            reason: "Stakeholder clarification",
          }),
        },
      );
      setData((current) =>
        current
          ? {
              ...current,
              items: current.items.map((entry) =>
                entry.id === updated.id ? updated : entry,
              ),
            }
          : current,
      );
      setAnalysisSummary(null);
      setEditing(null);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Clarification failed.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <p className="text-sm font-semibold text-[#d9ff76]">
        Requirement baseline
      </p>
      <h1 className="mt-3 text-4xl font-semibold">Requirements</h1>
      <p className="mt-4 max-w-2xl text-pretty text-base text-[#9b9b9b]">
        Review structured requirements, their sources, quality findings, and
        approval state.
      </p>
      {data && data.total > 0 && (
        <section className="mt-8 rounded-2xl border border-white/10 bg-[#181818] p-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold">Validation workflow</h2>
              <p className="mt-2 text-sm text-[#888]">
                Run the persisted quality graph and resume any clarification
                interrupt.
              </p>
            </div>
            <span className="rounded-full bg-white/5 px-3 py-1 text-xs uppercase text-[#d9ff76]">
              {workflow?.status ?? "not started"}
            </span>
          </div>
          {workflow?.status === "awaiting_clarification" ? (
            <form onSubmit={resumeWorkflow} className="mt-5 space-y-4">
              {workflowClarifications.map((value, index) => {
                const questionPosition =
                  workflow.state.clarification_indices?.indexOf(index) ?? -1;
                return (
                  <label key={index} className="block text-sm">
                    <span>
                      {questionPosition >= 0
                        ? workflow.state.clarification_questions?.[
                            questionPosition
                          ]
                        : "Confirmed requirement"}
                    </span>
                    <textarea
                      required
                      minLength={10}
                      rows={2}
                      value={value}
                      onChange={(event) =>
                        setWorkflowClarifications((current) =>
                          current.map((item, itemIndex) =>
                            itemIndex === index ? event.target.value : item,
                          ),
                        )
                      }
                      className="mt-2 w-full rounded-lg border border-white/10 bg-[#111] p-3 outline-none focus:border-[#d9ff76] focus:ring-2 focus:ring-[#d9ff76]/20"
                    />
                  </label>
                );
              })}
              <Button disabled={workflowBusy}>
                {workflowBusy ? (
                  <SpinnerGap className="animate-spin" />
                ) : (
                  <CheckCircle />
                )}
                Resume workflow
              </Button>
            </form>
          ) : (
            <div className="mt-5 flex flex-wrap items-center gap-4">
              <Button
                type="button"
                variant="secondary"
                onClick={startWorkflow}
                disabled={workflowBusy}
              >
                {workflowBusy ? (
                  <SpinnerGap className="animate-spin" />
                ) : (
                  <ArrowsClockwise />
                )}
                {workflow
                  ? "Run validation again"
                  : "Start validation workflow"}
              </Button>
              {workflow && (
                <p className="text-sm text-[#888]">
                  Iteration {workflow.state.iteration ?? 0} of{" "}
                  {workflow.state.max_iterations ?? 2}
                </p>
              )}
            </div>
          )}
        </section>
      )}
      {data && data.total > 0 && (
        <div className="mt-6">
          <Button
            onClick={analyze}
            disabled={analyzing}
            variant="secondary"
          >
            {analyzing ? (
              <SpinnerGap className="animate-spin" />
            ) : (
              <ClipboardText />
            )}{" "}
            {analyzing ? "Analyzing…" : "Analyze quality"}
          </Button>
          {analysisSummary && (
            <div
              role="status"
              aria-live="polite"
              className="mt-4 flex max-w-2xl gap-3 rounded-xl border border-emerald-300/20 bg-emerald-300/10 p-4 text-sm text-emerald-100"
            >
              <CheckCircle className="mt-0.5 shrink-0" size={20} />
              <p>
                Quality analysis complete. Reviewed{" "}
                {analysisSummary.requirements}{" "}
                {analysisSummary.requirements === 1
                  ? "requirement"
                  : "requirements"}
                ; found {analysisSummary.ambiguities}{" "}
                {analysisSummary.ambiguities === 1 ? "ambiguity" : "ambiguities"}
                {" and "}
                {analysisSummary.conflicts}{" "}
                {analysisSummary.conflicts === 1 ? "conflict" : "conflicts"}.
              </p>
            </div>
          )}
        </div>
      )}
      {error ? (
        <div
          role="alert"
          className="mt-10 flex gap-3 rounded-xl border border-red-300/20 bg-red-300/10 p-5 text-red-200"
        >
          <WarningCircle size={22} />
          {error}
        </div>
      ) : !data ? (
        <div className="mt-10 flex items-center gap-3 text-[#9b9b9b]">
          <SpinnerGap className="animate-spin" />
          Loading requirements…
        </div>
      ) : data.total === 0 ? (
        <section className="mt-10 rounded-2xl border border-white/10 bg-[#181818] p-8 text-center sm:p-12">
          <ClipboardText className="mx-auto text-[#d9ff76]" size={42} />
          <h2 className="mt-6 text-2xl font-semibold">No requirements yet</h2>
          <p className="mx-auto mt-3 max-w-lg text-[#9b9b9b]">
            Capture a stakeholder statement to create the first traceable
            requirement.
          </p>
          <Button asChild className="mt-8">
            <Link to={`/projects/${project.id}/interview`}>
              Start discovery
            </Link>
          </Button>
        </section>
      ) : (
        <div className="mt-10 space-y-4">
          {data.items.map((item) => (
            <article
              key={item.id}
              className="rounded-2xl border border-white/10 bg-[#181818] p-6 transition hover:border-white/20"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <span className="font-mono text-sm text-[#d9ff76]">
                  {item.requirement_code}
                </span>
                <span className="rounded-full bg-white/5 px-3 py-1 text-xs capitalize text-[#bcbcbc]">
                  {item.approval_status}
                </span>
              </div>
              <h2 className="mt-4 text-lg font-medium">{item.statement}</h2>
              <div className="mt-4 flex flex-wrap gap-2">
                {item.categories.map((category) => (
                  <span
                    key={category}
                    className="rounded-full bg-[#272727] px-2.5 py-1 text-xs text-[#bcbcbc]"
                  >
                    {category}
                  </span>
                ))}
              </div>
              <p className="mt-4 text-sm text-[#888]">
                Source: {item.source_stakeholder} · Confidence{" "}
                {Math.round(item.confidence * 100)}% · Version {item.version}
              </p>
              {item.quality_findings.length > 0 && (
                <div className="mt-4 space-y-2">
                  {item.quality_findings.map((finding, index) => (
                    <div
                      key={`${finding.kind}-${index}`}
                      className="rounded-lg border border-amber-200/10 bg-amber-200/5 p-3 text-sm"
                    >
                      <p className="font-medium capitalize text-amber-200">
                        {finding.kind}
                      </p>
                      <p className="mt-1 text-[#bcbcbc]">{finding.message}</p>
                      <p className="mt-1 text-[#aaa]">{finding.question}</p>
                    </div>
                  ))}
                </div>
              )}
              {item.clarification_status === "resolved" && (
                <p className="mt-4 flex items-center gap-2 text-sm text-emerald-300">
                  <CheckCircle /> Clarification resolved and version history
                  preserved.
                </p>
              )}
              {editing === item.id ? (
                <form
                  onSubmit={(event) => saveClarification(event, item)}
                  className="mt-5 rounded-xl border border-[#d9ff76]/20 bg-[#111] p-4"
                >
                  <label
                    className="text-sm font-medium"
                    htmlFor={`statement-${item.id}`}
                  >
                    Clarified requirement
                  </label>
                  <textarea
                    id={`statement-${item.id}`}
                    required
                    minLength={10}
                    maxLength={5000}
                    rows={3}
                    value={clarification}
                    onChange={(event) => setClarification(event.target.value)}
                    className="mt-2 w-full rounded-lg border border-white/10 bg-[#181818] p-3 outline-none focus:border-[#d9ff76] focus:ring-2 focus:ring-[#d9ff76]/20"
                  />
                  <label
                    className="mt-4 block text-sm font-medium"
                    htmlFor={`criterion-${item.id}`}
                  >
                    Measurable acceptance criterion
                  </label>
                  <textarea
                    id={`criterion-${item.id}`}
                    required
                    minLength={5}
                    rows={2}
                    value={criterion}
                    onChange={(event) => setCriterion(event.target.value)}
                    className="mt-2 w-full rounded-lg border border-white/10 bg-[#181818] p-3 outline-none focus:border-[#d9ff76] focus:ring-2 focus:ring-[#d9ff76]/20"
                  />
                  <div className="mt-4 flex flex-wrap gap-3">
                    <Button disabled={saving}>
                      {saving ? (
                        <SpinnerGap className="animate-spin" />
                      ) : (
                        <CheckCircle />
                      )}{" "}
                      {saving ? "Saving…" : "Save clarification"}
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => setEditing(null)}
                      disabled={saving}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              ) : (
                item.quality_findings.length > 0 && (
                  <Button
                    type="button"
                    variant="secondary"
                    className="mt-5"
                    onClick={() => beginClarification(item)}
                  >
                    <PencilSimple /> Resolve clarification
                  </Button>
                )
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
