import {
  CheckCircle,
  ClipboardText,
  PencilSimple,
  SpinnerGap,
  Trash,
  WarningCircle,
} from "@phosphor-icons/react";
import { type FormEvent, useEffect, useState } from "react";
import { Link, useOutletContext } from "react-router-dom";

import { apiRequest } from "@/api/client";
import type { Requirement, RequirementList } from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

const findingLabels: Record<string, string> = {
  ambiguity: "Ambiguous",
  incomplete: "Incomplete",
  conflict: "Possible conflict",
  duplicate: "Possible duplicate",
};

const fieldClass =
  "mt-2 w-full rounded-lg border border-white/10 bg-[#181818] p-3 outline-none focus:border-[#d9ff76] focus:ring-2 focus:ring-[#d9ff76]/20";

export function RequirementsPage() {
  const { project, reload } = useOutletContext<ProjectOutletContext>();
  const path = `/projects/${project.id}/requirements`;
  const [data, setData] = useState<RequirementList | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [editing, setEditing] = useState<{
    id: string;
    statement: string;
    criteria: string;
  } | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setData(null);
    setEditing(null);
    setError("");
    setNotice("");
    apiRequest<RequirementList>(path, { authenticated: true, signal: controller.signal })
      .then(setData)
      .catch((reason: Error) => {
        if (!controller.signal.aborted) setError(reason.message);
      });
    return () => controller.abort();
  }, [path]);

  async function save(event: FormEvent<HTMLFormElement>, item: Requirement) {
    event.preventDefault();
    if (!editing || busy) return;

    setBusy(true);
    setError("");
    setNotice("");
    try {
      const updated = await apiRequest<Requirement>(`${path}/${item.id}`, {
        method: "PATCH",
        authenticated: true,
        body: JSON.stringify({
          statement: editing.statement.trim(),
          acceptance_criteria:
            editing.criteria === item.acceptance_criteria.join("\n")
              ? undefined
              : editing.criteria.split("\n").map((line) => line.trim()).filter(Boolean),
        }),
      });
      setData((current) =>
        current && { ...current, items: current.items.map((row) => row.id === item.id ? updated : row) },
      );
      setEditing(null);
      setNotice(`${item.requirement_code} saved.`);
      setData(await apiRequest<RequirementList>(path, { authenticated: true }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not update requirement.");
    } finally {
      setBusy(false);
    }
  }

  async function remove(item: Requirement) {
    if (busy || !window.confirm(`Delete ${item.requirement_code} from the project?`)) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const updated = await apiRequest<RequirementList>(`${path}/${item.id}`, {
        method: "DELETE",
        authenticated: true,
      });
      setData(updated);
      if (editing?.id === item.id) setEditing(null);
      setNotice(`${item.requirement_code} deleted.`);
      void reload();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not delete requirement.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1 className="text-4xl font-semibold">Requirements</h1>
      {error && (
        <p role="alert" className="mt-6 flex gap-3 rounded-xl border border-red-300/20 bg-red-300/10 p-4 text-red-200">
          <WarningCircle aria-hidden="true" size={22} />
          {error}
        </p>
      )}
      <div role="status" aria-live="polite">
        {notice && <p className="mt-6 text-sm text-emerald-300">{notice}</p>}
        {!data && !error && (
          <p className="mt-8 flex items-center gap-3 text-[#9b9b9b]">
            <SpinnerGap aria-hidden="true" className="animate-spin" />
            Loading requirements…
          </p>
        )}
      </div>
      {data?.total === 0 && (
        <section className="mt-8 rounded-2xl border border-white/10 bg-[#181818] p-8 text-center sm:p-12">
          <ClipboardText aria-hidden="true" className="mx-auto text-[#d9ff76]" size={42} />
          <h2 className="mt-6 text-2xl font-semibold">No requirements yet</h2>
          <Button asChild className="mt-6">
            <Link to={`/projects/${project.id}/interview`}>Open Interview</Link>
          </Button>
        </section>
      )}
      {!!data?.total && (
        <div className="mt-8 space-y-4">
          {data.items.map((item) => (
            <article
              key={item.id}
              className="rounded-2xl border border-white/10 bg-[#181818] p-5 sm:p-6"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-sm text-[#d9ff76]">{item.requirement_code}</span>
                </div>
                <div className="flex shrink-0 items-center gap-1">
                  {editing?.id !== item.id && (
                    <Button
                      type="button"
                      size="small"
                      variant="ghost"
                      aria-label={`Edit ${item.requirement_code}`}
                      disabled={busy}
                      onClick={() => {
                        setEditing({
                          id: item.id,
                          statement: item.statement,
                          criteria: item.acceptance_criteria.join("\n"),
                        });
                        setNotice("");
                        setError("");
                      }}
                    >
                      <PencilSimple aria-hidden="true" />
                      Edit
                    </Button>
                  )}
                  <Button
                    type="button"
                    size="small"
                    variant="ghost"
                    className="size-9 px-0 hover:bg-red-300/10 hover:text-red-200"
                    aria-label={`Delete ${item.requirement_code}`}
                    title={`Delete ${item.requirement_code}`}
                    disabled={busy}
                    onClick={() => void remove(item)}
                  >
                    <Trash aria-hidden="true" size={17} />
                  </Button>
                </div>
              </div>
              <h2 className="mt-3 text-lg font-medium">{item.statement}</h2>
              <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-2 text-sm text-[#9b9b9b]">
                {item.categories.map((category) => (
                  <span key={category} className="rounded-full bg-[#272727] px-2.5 py-1 text-xs text-[#bcbcbc]">
                    {category}
                  </span>
                ))}
                <span>Source {item.source_stakeholder} · Version {item.version}</span>
              </div>
              {item.quality_findings.length > 0 ? (
                <ul className="mt-4 space-y-2">
                  {item.quality_findings.map((finding, index) => (
                    <li
                      key={`${finding.kind}-${index}`}
                      className="rounded-lg border border-amber-200/10 bg-amber-200/5 p-3 text-sm"
                    >
                      <p className="font-medium text-amber-200">
                        {findingLabels[finding.kind] ?? finding.kind}
                      </p>
                      <p className="mt-1 text-[#bcbcbc]">{finding.message} {finding.question}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-4 flex items-center gap-2 text-sm text-emerald-300">
                  <CheckCircle aria-hidden="true" /> No wording issues found
                </p>
              )}
              {editing?.id === item.id ? (
                <form onSubmit={(event) => void save(event, item)} className="mt-5 rounded-xl border border-white/10 bg-[#111] p-4">
                  <label htmlFor={`statement-${item.id}`} className="text-sm font-medium">Requirement</label>
                  <textarea
                    id={`statement-${item.id}`}
                    required
                    minLength={10}
                    maxLength={5000}
                    rows={3}
                    value={editing.statement}
                    onChange={(event) => setEditing({ ...editing, statement: event.target.value })}
                    className={fieldClass}
                  />
                  <details className="mt-4 text-sm" open={item.acceptance_criteria.length > 0 || undefined}>
                    <summary className="cursor-pointer text-[#bcbcbc]">Acceptance criteria (optional)</summary>
                    <textarea
                      aria-label="Acceptance criteria (optional)"
                      rows={2}
                      placeholder="Enter one criterion per line."
                      value={editing.criteria}
                      onChange={(event) => setEditing({ ...editing, criteria: event.target.value })}
                      className={fieldClass}
                    />
                  </details>
                  <div className="mt-4 flex flex-wrap gap-3">
                    <Button type="submit" disabled={busy || editing.statement.trim().length < 10}>
                      {busy ? "Saving…" : "Save"}
                    </Button>
                    <Button type="button" variant="secondary" onClick={() => setEditing(null)} disabled={busy}>
                      Cancel
                    </Button>
                  </div>
                </form>
              ) : item.acceptance_criteria.length > 0 ? (
                <details className="mt-4 text-sm text-[#bcbcbc]">
                  <summary className="cursor-pointer">Acceptance criteria</summary>
                  <ul className="mt-2 list-disc space-y-1 pl-5">
                    {item.acceptance_criteria.map((criterion, index) => <li key={index}>{criterion}</li>)}
                  </ul>
                </details>
              ) : null}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
