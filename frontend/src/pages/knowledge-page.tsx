import {
  FileArrowUp,
  MagnifyingGlass,
  SpinnerGap,
  WarningCircle,
} from "@phosphor-icons/react";
import { FormEvent, useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";

import { apiRequest } from "@/api/client";
import type {
  ComplianceMapping,
  CompliancePassage,
  EvidenceChunk,
  KnowledgeDocument,
} from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

function PolicyPassage({ passage, showQuote = true }: { passage: CompliancePassage; showQuote?: boolean }) {
  return (
    <figure className="rounded-lg border border-white/10 bg-[#181818] p-3">
      <figcaption className="text-xs font-medium text-[#d9ff76]">
        {passage.filename} · v{passage.version}{passage.section && ` · ${passage.section}`}
      </figcaption>
      {showQuote && <blockquote className="mt-2 break-words text-sm text-[#d1d1d1]">{passage.content}</blockquote>}
    </figure>
  );
}

type PolicyAnswer = { answer: string | null; answer_source: EvidenceChunk | null; items: EvidenceChunk[] };

export function KnowledgePage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [policyAnswer, setPolicyAnswer] = useState<PolicyAnswer | null>(null);
  const [query, setQuery] = useState("");
  const [sourceKind, setSourceKind] = useState<"file" | "text">("file");
  const [savedSource, setSavedSource] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [mappings, setMappings] = useState<ComplianceMapping[]>([]);

  useEffect(() => {
    Promise.all([
      apiRequest<KnowledgeDocument[]>(
        `/projects/${project.id}/knowledge/documents`,
        { authenticated: true },
      ),
      apiRequest<{ items: ComplianceMapping[] }>(
        `/projects/${project.id}/compliance`,
        { authenticated: true },
      ),
    ])
      .then(([loadedDocuments, compliance]) => {
        setDocuments(loadedDocuments);
        setMappings(compliance.items);
      })
      .catch((reason: Error) => setError(reason.message));
  }, [project.id]);

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setSavedSource("");
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    try {
      if (sourceKind === "text") {
        const title = String(form.get("title") ?? "").trim().replace(/\.txt$/i, "");
        const text = String(form.get("text") ?? "").trim();
        if (!title || !text) throw new Error("Enter a source title and paste the policy text.");
        form.delete("title");
        form.delete("text");
        form.set("file", new Blob([text], { type: "text/plain" }), `${title}.txt`);
      }
      const document = await apiRequest<KnowledgeDocument>(
        `/projects/${project.id}/knowledge/documents`,
        { method: "POST", authenticated: true, body: form },
      );
      setDocuments((items) => [document, ...items]);
      setSavedSource(document.filename);
      formElement.reset();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not add evidence.");
    } finally {
      setBusy(false);
    }
  }

  async function retrieve(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setPolicyAnswer(null);
    try {
      const result = await apiRequest<PolicyAnswer>(
        `/projects/${project.id}/knowledge/retrieve`,
        {
          method: "POST",
          authenticated: true,
          body: JSON.stringify({ query, limit: 5 }),
        },
      );
      setPolicyAnswer(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Retrieval failed.");
    } finally {
      setBusy(false);
    }
  }

  async function analyzeCompliance() {
    setBusy(true);
    setError("");
    try {
      const result = await apiRequest<{ items: ComplianceMapping[] }>(
        `/projects/${project.id}/compliance/analyze`,
        { method: "POST", authenticated: true },
      );
      setMappings(result.items);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Compliance analysis failed.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <p className="text-sm font-semibold text-[#d9ff76]">Evidence mapping</p>
      <h1 className="mt-3 text-4xl font-semibold">Compliance</h1>
      <p className="mt-4 max-w-2xl text-[#9b9b9b]">
        Add a policy source and look up passages that relate to your requirements.
      </p>
      {error && (
        <p
          role="alert"
          className="mt-5 flex gap-2 rounded-lg bg-red-300/10 p-3 text-red-200"
        >
          <WarningCircle />
          {error}
        </p>
      )}
      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <form
          onSubmit={upload}
          className="rounded-2xl border border-white/10 bg-[#181818] p-6"
        >
          <h2 className="text-xl font-semibold">Add evidence</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button type="button" size="small" variant="secondary" aria-pressed={sourceKind === "file"} disabled={busy} onClick={() => setSourceKind("file")}>
              Upload a file
            </Button>
            <Button type="button" size="small" variant="secondary" aria-pressed={sourceKind === "text"} disabled={busy} onClick={() => setSourceKind("text")}>
              Paste text
            </Button>
          </div>
          {sourceKind === "file" ? (
            <label className="mt-5 block text-sm font-medium">
              Evidence document
              <input
                required
                name="file"
                type="file"
                accept=".pdf,.docx,.txt"
                className="mt-2 block w-full rounded-lg border border-white/10 bg-[#111] p-3 text-sm file:mr-3 file:rounded-md file:border-0 file:bg-[#d9ff76] file:px-3 file:py-2 file:font-semibold"
              />
            </label>
          ) : (
            <>
              <label className="mt-5 block text-sm font-medium">
                Source title
                <input name="title" required maxLength={160} placeholder="Loan intake policy" className="mt-2 block w-full rounded-lg border border-white/10 bg-[#111] p-3" />
              </label>
              <label className="mt-4 block text-sm font-medium">
                Policy text
                <textarea name="text" required rows={5} placeholder="Paste the relevant policy text." className="mt-2 block w-full rounded-lg border border-white/10 bg-[#111] p-3" />
              </label>
            </>
          )}
          <div className="mt-4 grid grid-cols-2 gap-3">
            <input
              required
              name="jurisdiction"
              defaultValue={project.jurisdiction}
              aria-label="Jurisdiction"
              className="rounded-lg border border-white/10 bg-[#111] p-3 focus:border-[#d9ff76] focus:outline-none"
            />
            <input
              required
              name="version"
              defaultValue="1.0"
              aria-label="Version"
              className="rounded-lg border border-white/10 bg-[#111] p-3 focus:border-[#d9ff76] focus:outline-none"
            />
          </div>
          <Button disabled={busy} className="mt-5 w-full">
            {busy ? <SpinnerGap className="animate-spin" /> : <FileArrowUp />}
            {sourceKind === "file" ? "Index document" : "Index text"}
          </Button>
          {savedSource && <p role="status" className="mt-3 text-sm text-[#d9ff76]">Indexed {savedSource}.</p>}
        </form>
        <form
          onSubmit={retrieve}
          className="rounded-2xl border border-white/10 bg-[#181818] p-6"
        >
          <h2 className="text-xl font-semibold">Ask about your policy</h2>
          <textarea
            aria-label="Evidence search"
            required
            minLength={3}
            rows={4}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="What evidence governs applicant consent?"
            className="mt-5 w-full rounded-lg border border-white/10 bg-[#111] p-3 focus:border-[#d9ff76] focus:outline-none"
          />
          <Button
            disabled={busy || documents.length === 0}
            variant="secondary"
            className="mt-5 w-full"
          >
            <MagnifyingGlass />
            Get answer with evidence
          </Button>
          {policyAnswer && (
            <section className="mt-5 space-y-3" aria-live="polite">
              <h3 className="font-semibold">Answer</h3>
              <p className="text-sm text-[#e1e1e1]">{policyAnswer.answer ?? "I couldn’t find a clause that directly answers this question."}</p>
              {policyAnswer.answer_source && (
                <PolicyPassage
                  passage={{ ...policyAnswer.answer_source, id: policyAnswer.answer_source.chunk_id }}
                  showQuote={policyAnswer.answer !== policyAnswer.answer_source.content}
                />
              )}
              {!policyAnswer.answer_source && policyAnswer.items.length > 0 && (
                <details className="text-sm">
                  <summary className="cursor-pointer text-[#bcbcbc]">See nearby clauses</summary>
                  <div className="mt-2 space-y-2">
                    {policyAnswer.items.map((item) => <PolicyPassage key={`${item.chunk_id}/${item.content}`} passage={{ ...item, id: item.chunk_id }} />)}
                  </div>
                </details>
              )}
            </section>
          )}
        </form>
      </div>
      <section className="mt-8">
        <h2 className="text-xl font-semibold">Indexed sources</h2>
        {documents.length === 0 ? (
          <p className="mt-4 rounded-xl border border-dashed border-white/10 p-6 text-[#888]">
            No evidence documents indexed.
          </p>
        ) : (
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {documents.map((document) => (
              <article
                key={document.id}
                className="rounded-xl border border-white/10 bg-[#181818] p-4"
              >
                <p className="font-medium">{document.filename}</p>
                <p className="mt-2 text-sm text-[#888]">
                  {document.jurisdiction} · v{document.version} ·{" "}
                  {document.status}
                </p>
              </article>
            ))}
          </div>
        )}
      </section>
      <section className="mt-8 rounded-2xl border border-white/10 bg-[#181818] p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">Requirements and policy evidence</h2>
            <p className="mt-2 max-w-xl text-sm text-[#bcbcbc]">
              Compare requirements with policy clauses. Clear matches are labeled by AI. Partial or uncertain matches are flagged for review.
            </p>
          </div>
          <Button
            onClick={analyzeCompliance}
            disabled={busy || documents.length === 0}
            variant="secondary"
          >
            {busy ? "Working…" : "Review policy evidence with AI"}
          </Button>
        </div>
        {mappings.length === 0 ? (
          <p className="mt-5 text-sm text-[#9b9b9b]">Add a policy source, then match it against your saved requirements.</p>
        ) : (
          <div className="mt-5 space-y-3">
            {mappings.map((mapping) => {
              const first = mapping.passages[0];
              const current = mapping.ai_reviewed && ["ai_matched", "needs_human_review", "no_matching_evidence"].includes(mapping.status);
              const matched = current && !mapping.needs_refresh && mapping.status === "ai_matched";
              return (
                <article key={mapping.id} className="rounded-xl bg-[#111] p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="font-mono text-sm text-[#d9ff76]">{mapping.requirement_code}</p>
                    <p className={`rounded-full px-2.5 py-1 text-xs font-medium ${matched ? "bg-emerald-300/10 text-emerald-200" : "bg-white/5 text-[#d1d1d1]"}`}>
                      {mapping.needs_refresh ? "Requirement changed" : !current ? "Run updated review" : matched ? "AI matched" : first ? "Human review needed" : "No policy match"}
                    </p>
                  </div>
                  <h3 className="mt-2 font-medium">{mapping.requirement_statement}</h3>
                  {!current || mapping.needs_refresh ? (
                    <p className="mt-3 text-sm text-[#bcbcbc]">Run the AI review to check the current requirement against your sources.</p>
                  ) : (
                    <div className="mt-3 space-y-2">
                      <p className="text-sm text-[#bcbcbc]">{mapping.rationale}</p>
                      {first && <PolicyPassage passage={first} />}
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}
      </section>

    </div>
  );
}
