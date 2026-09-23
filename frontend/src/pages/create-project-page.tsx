import { ArrowLeft, ArrowRight } from "@phosphor-icons/react";
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError, apiRequest } from "@/api/client";
import type { Project, ProjectCreate } from "@/api/types";
import { InputField, TextareaField } from "@/components/form-field";
import { Button } from "@/components/ui/button";
import { WorkspaceHeader } from "@/components/workspace-header";

const initialForm: ProjectCreate = {
  name: "",
  summary: "",
  product_type: "Digital personal loan origination",
  jurisdiction: "India",
  primary_stakeholder: { name: "", role: "", organization: "" },
};

export function CreateProjectPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function updateField(field: keyof Omit<ProjectCreate, "primary_stakeholder">, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function updateStakeholder(field: "name" | "role" | "organization", value: string) {
    setForm((current) => ({
      ...current,
      primary_stakeholder: { ...current.primary_stakeholder!, [field]: value },
    }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (form.summary.trim().length < 30) {
      setError("Describe the project outcome in at least 30 characters.");
      return;
    }
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        primary_stakeholder: form.primary_stakeholder?.name
          ? form.primary_stakeholder
          : undefined,
      };
      const project = await apiRequest<Project>("/projects", {
        method: "POST",
        authenticated: true,
        body: JSON.stringify(payload),
      });
      navigate(`/projects/${project.id}/overview`);
    } catch (requestError) {
      setError(
        requestError instanceof ApiError
          ? requestError.message
          : "The project could not be saved. Your input is preserved.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#131209]">
      <WorkspaceHeader />
      <main className="mx-auto max-w-3xl px-6 py-12">
        <Link className="inline-flex items-center gap-2 rounded-md text-sm font-semibold text-[#9b9b9b] hover:text-white" to="/dashboard">
          <ArrowLeft aria-hidden="true" /> Back to dashboard
        </Link>
        <p className="mt-10 text-sm font-semibold text-[#d9ff76]">New project</p>
        <h1 className="mt-3 text-balance text-4xl font-semibold">Define the discovery starting point.</h1>
        <p className="mt-4 max-w-2xl text-pretty text-base text-[#9b9b9b]">
          Capture enough context for a focused stakeholder interview. Requirements and evidence will be added later in the workflow.
        </p>

        <form className="mt-10 space-y-8" noValidate onSubmit={submit}>
          <section className="rounded-2xl border border-white/10 bg-[#181818] p-6">
            <h2 className="text-xl font-semibold">Project context</h2>
            <div className="mt-6 space-y-6">
              <InputField disabled={submitting} label="Project name" name="name" onChange={(event) => updateField("name", event.target.value)} required value={form.name} />
              <TextareaField disabled={submitting} hint={`${form.summary.length} of 2000 characters`} label="Desired outcome" maxLength={2000} name="summary" onChange={(event) => updateField("summary", event.target.value)} placeholder="Replace manual application intake with a controlled workflow that supports document review, eligibility checks, and traceable decisions." required value={form.summary} />
              <div className="grid gap-6 sm:grid-cols-2">
                <InputField disabled={submitting} label="Product type" name="product_type" onChange={(event) => updateField("product_type", event.target.value)} required value={form.product_type} />
                <InputField disabled={submitting} label="Primary jurisdiction" name="jurisdiction" onChange={(event) => updateField("jurisdiction", event.target.value)} required value={form.jurisdiction} />
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-white/10 bg-[#181818] p-6">
            <h2 className="text-xl font-semibold">Primary stakeholder</h2>
            <p className="mt-2 text-sm text-[#8f8f8f]">Optional for now. Add the person who will begin discovery.</p>
            <div className="mt-6 grid gap-6 sm:grid-cols-2">
              <InputField disabled={submitting} label="Name" name="stakeholder_name" onChange={(event) => updateStakeholder("name", event.target.value)} value={form.primary_stakeholder?.name} />
              <InputField disabled={submitting} label="Role" name="stakeholder_role" onChange={(event) => updateStakeholder("role", event.target.value)} placeholder="Loan operations manager" value={form.primary_stakeholder?.role} />
              <InputField className="sm:col-span-2" disabled={submitting} label="Organization" name="organization" onChange={(event) => updateStakeholder("organization", event.target.value)} value={form.primary_stakeholder?.organization} />
            </div>
          </section>

          {error && <div className="rounded-lg border border-[#ff9b8f]/30 bg-[#ff9b8f]/10 p-3 text-sm text-[#ffb8af]" role="alert">{error}</div>}
          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <Button asChild variant="secondary"><Link to="/dashboard">Cancel</Link></Button>
            <Button disabled={submitting || !form.name || !form.summary || !form.jurisdiction} type="submit">
              {submitting ? "Creating project" : "Create project"} {!submitting && <ArrowRight aria-hidden="true" />}
            </Button>
          </div>
        </form>
      </main>
    </div>
  );
}
