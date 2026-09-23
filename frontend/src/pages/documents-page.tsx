import { DownloadSimple, FileText, SpinnerGap, WarningCircle } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { apiRequest, getAccessToken } from "@/api/client";
import type { Artifact } from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export function DocumentsPage() {
  const { project } = useOutletContext<ProjectOutletContext>(); const [items, setItems] = useState<Artifact[]>([]); const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  useEffect(() => { apiRequest<{ items: Artifact[] }>(`/projects/${project.id}/artifacts`, { authenticated: true }).then((data) => setItems(data.items)).catch((reason: Error) => setError(reason.message)); }, [project.id]);
  async function generate() { setBusy(true); setError(""); try { const data = await apiRequest<{ items: Artifact[] }>(`/projects/${project.id}/artifacts/generate`, { method: "POST", authenticated: true }); setItems(data.items); } catch (reason) { setError(reason instanceof Error ? reason.message : "Generation failed."); } finally { setBusy(false); } }
  async function download(item: Artifact) { const response = await fetch(`${API_URL}/projects/${project.id}/artifacts/${item.id}/download`, { headers: { Authorization: `Bearer ${getAccessToken()}` } }); if (!response.ok) { setError("Download failed."); return; } const url = URL.createObjectURL(await response.blob()); const link = document.createElement("a"); link.href = url; link.download = `${item.artifact_type}.html`; link.click(); URL.revokeObjectURL(url); }
  return <div><p className="text-sm font-semibold text-[#d9ff76]">Project artefacts</p><h1 className="mt-3 text-4xl font-semibold">Documents and traceability</h1><p className="mt-4 max-w-2xl text-[#9b9b9b]">Generate structured, versioned outputs from approved project data while preserving source requirement IDs.</p><Button onClick={generate} disabled={busy} className="mt-6">{busy ? <SpinnerGap className="animate-spin" /> : <FileText />}Generate artefact set</Button>{error && <p role="alert" className="mt-5 flex gap-2 text-red-200"><WarningCircle />{error}</p>}{items.length === 0 ? <p className="mt-8 rounded-xl border border-dashed border-white/10 p-8 text-center text-[#888]">No generated artefacts yet.</p> : <div className="mt-8 grid gap-4 sm:grid-cols-2">{items.map((item) => <article key={item.id} className="rounded-2xl border border-white/10 bg-[#181818] p-6 transition hover:border-white/20"><FileText className="text-[#d9ff76]" size={28} /><h2 className="mt-4 text-lg font-semibold">{item.title}</h2><p className="mt-2 text-sm text-[#888]">Version {item.version} · {item.source_requirement_ids.length} linked requirements</p><Button onClick={() => download(item)} variant="secondary" className="mt-5"><DownloadSimple />Download HTML</Button></article>)}</div>}</div>;
}
