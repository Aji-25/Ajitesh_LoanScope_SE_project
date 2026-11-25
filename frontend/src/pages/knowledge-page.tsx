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
  EvidenceChunk,
  KnowledgeDocument,
} from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

export function KnowledgePage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [evidence, setEvidence] = useState<EvidenceChunk[]>([]);
  const [query, setQuery] = useState("");
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
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    try {
      const document = await apiRequest<KnowledgeDocument>(
        `/projects/${project.id}/knowledge/documents`,
        { method: "POST", authenticated: true, body: form },
      );
      setDocuments((items) => [document, ...items]);
      formElement.reset();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Upload failed.");
    } finally {
      setBusy(false);
    }
  }

  async function retrieve(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const result = await apiRequest<{ items: EvidenceChunk[] }>(
        `/projects/${project.id}/knowledge/retrieve`,
        {
          method: "POST",
          authenticated: true,
          body: JSON.stringify({ query, limit: 5 }),
        },
      );
      setEvidence(result.items);
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
      <h1 className="mt-3 text-4xl font-semibold">Knowledge base</h1>
      <p className="mt-4 max-w-2xl text-[#9b9b9b]">
        Index regulatory guidance and internal policy with source metadata, then
        test retrieval independently.
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
          <h2 className="text-xl font-semibold">Upload evidence</h2>
          <label htmlFor="evidence-file" className="mt-5 block text-sm font-medium">
            Evidence document
          </label>
          <input
            id="evidence-file"
            required
            name="file"
            type="file"
            accept=".pdf,.docx,.txt"
            className="mt-2 block w-full rounded-lg border border-white/10 bg-[#111] p-3 text-sm file:mr-3 file:rounded-md file:border-0 file:bg-[#d9ff76] file:px-3 file:py-2 file:font-semibold"
          />
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
            Index document
          </Button>
        </form>
        <form
          onSubmit={retrieve}
          className="rounded-2xl border border-white/10 bg-[#181818] p-6"
        >
          <h2 className="text-xl font-semibold">Test retrieval</h2>
          <textarea
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
            Retrieve evidence
          </Button>
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
            <h2 className="text-xl font-semibold">Compliance mapping</h2>
            <p className="mt-2 text-sm text-[#888]">
              Ground each requirement in retrieved evidence.
            </p>
          </div>
          <Button
            onClick={analyzeCompliance}
            disabled={busy || documents.length === 0}
            variant="secondary"
          >
            Analyze compliance
          </Button>
        </div>
        {mappings.length > 0 && (
          <div className="mt-5 space-y-3">
            {mappings.map((mapping) => (
              <article key={mapping.id} className="rounded-xl bg-[#111] p-4">
                <div className="flex flex-wrap justify-between gap-3">
                  <p className="font-medium">{mapping.obligation}</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="rounded-full bg-[#d9ff76]/10 px-2 py-1 text-xs uppercase text-[#d9ff76]">
                      {mapping.applicability}
                    </span>
                    <span className="rounded-full bg-amber-300/10 px-2 py-1 text-xs uppercase text-amber-200">
                      {mapping.gap_status.replace("_", " ")}
                    </span>
                  </div>
                </div>
                <p className="mt-2 text-sm text-[#9b9b9b]">
                  {mapping.rationale}
                </p>
                <p className="mt-2 text-xs text-[#888]">
                  Confidence {Math.round(mapping.confidence * 100)}%
                  {mapping.human_review_required
                    ? " · Human review required"
                    : ""}
                </p>
                {mapping.citations.map((citation, index) => (
                  <p
                    key={`${citation.filename}-${index}`}
                    className="mt-2 text-xs text-[#aaa]"
                  >
                    {citation.filename} · {citation.section} · p.
                    {citation.page ?? "n/a"} · v{citation.version}
                  </p>
                ))}
              </article>
            ))}
          </div>
        )}
      </section>
      {evidence.length > 0 && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">Retrieved evidence</h2>
          <div className="mt-4 space-y-3">
            {evidence.map((item) => (
              <article
                key={item.chunk_id}
                className="rounded-xl border border-[#d9ff76]/15 bg-[#181818] p-5"
              >
                <p className="text-sm font-semibold text-[#d9ff76]">
                  {item.filename} · {item.section} ·{" "}
                  {Math.round(item.score * 100)}%
                </p>
                <p className="mt-3 text-sm text-[#bcbcbc]">{item.content}</p>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
