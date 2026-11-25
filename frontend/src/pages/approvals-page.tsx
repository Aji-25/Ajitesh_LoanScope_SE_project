import { CheckSquare, SpinnerGap, WarningCircle } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { apiRequest } from "@/api/client";
import type { Approval } from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

export function ApprovalsPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const [items, setItems] = useState<Approval[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [activeDecision, setActiveDecision] = useState<{
    id: string;
    action: "approve" | "reject" | "edit" | "regenerate";
  } | null>(null);
  const [comment, setComment] = useState("");
  const [editedOutcome, setEditedOutcome] = useState("");
  useEffect(() => {
    apiRequest<{ items: Approval[] }>(`/projects/${project.id}/approvals`, {
      authenticated: true,
    })
      .then((data) => setItems(data.items))
      .catch((reason: Error) => setError(reason.message));
  }, [project.id]);
  async function prepare() {
    setBusy(true);
    setError("");
    try {
      const data = await apiRequest<{ items: Approval[] }>(
        `/projects/${project.id}/approvals/prepare`,
        { method: "POST", authenticated: true },
      );
      setItems(data.items);
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Could not prepare approvals.",
      );
    } finally {
      setBusy(false);
    }
  }
  async function decide(
    id: string,
    action: "approve" | "reject" | "edit" | "regenerate",
  ) {
    setBusy(true);
    setError("");
    try {
      const updated = await apiRequest<Approval>(
        `/projects/${project.id}/approvals/${id}/decision`,
        {
          method: "POST",
          authenticated: true,
          body: JSON.stringify({
            action,
            comment,
            edits:
              action === "edit" ? { authoritative_text: editedOutcome } : {},
          }),
        },
      );
      setItems((current) =>
        current.map((item) => (item.id === id ? updated : item)),
      );
      setActiveDecision(null);
      setComment("");
      setEditedOutcome("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Decision failed.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <div>
      <p className="text-sm font-semibold text-[#d9ff76]">Human review</p>
      <h1 className="mt-3 text-4xl font-semibold">Approvals</h1>
      <p className="mt-4 max-w-2xl text-[#9b9b9b]">
        Review durable decision requests. Every action records the reviewer,
        comment, timestamp, and workflow thread.
      </p>
      {error && (
        <p role="alert" className="mt-5 flex gap-2 text-red-200">
          <WarningCircle />
          {error}
        </p>
      )}
      <Button onClick={prepare} disabled={busy} className="mt-6">
        {busy && <SpinnerGap className="animate-spin" />}
        Refresh approval requests
      </Button>
      {items.length === 0 ? (
        <section className="mt-10 rounded-2xl border border-white/10 bg-[#181818] p-10 text-center">
          <CheckSquare className="mx-auto text-[#d9ff76]" size={42} />
          <h2 className="mt-5 text-2xl font-semibold">
            No decisions are waiting
          </h2>
          <p className="mt-3 text-[#888]">
            Prepare a baseline approval after requirements are reviewed.
          </p>
        </section>
      ) : (
        <div className="mt-8 space-y-4">
          {items.map((item) => (
            <article
              key={item.id}
              className="rounded-2xl border border-white/10 bg-[#181818] p-6"
            >
              <div className="flex flex-wrap justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold">{item.title}</h2>
                  <p className="mt-2 text-sm text-[#888]">
                    Assigned to {item.assigned_role}
                  </p>
                </div>
                <span className="rounded-full bg-white/5 px-3 py-1 text-xs uppercase text-[#d9ff76]">
                  {item.status}
                </span>
              </div>
              {item.status === "pending" ? (
                activeDecision?.id === item.id ? (
                  <form
                    className="mt-5 rounded-xl border border-white/10 bg-[#111] p-4"
                    onSubmit={(event) => {
                      event.preventDefault();
                      void decide(item.id, activeDecision.action);
                    }}
                  >
                    <p className="font-medium capitalize">
                      {activeDecision.action} decision
                    </p>
                    <label
                      htmlFor={`comment-${item.id}`}
                      className="mt-4 block text-sm"
                    >
                      Review comment
                    </label>
                    <textarea
                      id={`comment-${item.id}`}
                      required
                      minLength={2}
                      maxLength={1000}
                      rows={3}
                      value={comment}
                      onChange={(event) => setComment(event.target.value)}
                      className="mt-2 w-full rounded-lg border border-white/10 bg-[#181818] p-3 outline-none focus:border-[#d9ff76] focus:ring-2 focus:ring-[#d9ff76]/20"
                    />
                    {activeDecision.action === "edit" && (
                      <>
                        <label
                          htmlFor={`edit-${item.id}`}
                          className="mt-4 block text-sm"
                        >
                          Edited authoritative outcome
                        </label>
                        <textarea
                          id={`edit-${item.id}`}
                          required
                          minLength={3}
                          rows={3}
                          value={editedOutcome}
                          onChange={(event) =>
                            setEditedOutcome(event.target.value)
                          }
                          className="mt-2 w-full rounded-lg border border-white/10 bg-[#181818] p-3 outline-none focus:border-[#d9ff76] focus:ring-2 focus:ring-[#d9ff76]/20"
                        />
                      </>
                    )}
                    <div className="mt-4 flex gap-2">
                      <Button
                        disabled={
                          busy ||
                          comment.trim().length < 2 ||
                          (activeDecision.action === "edit" &&
                            editedOutcome.trim().length < 3)
                        }
                      >
                        {busy && <SpinnerGap className="animate-spin" />}Submit
                        decision
                      </Button>
                      <Button
                        type="button"
                        variant="secondary"
                        disabled={busy}
                        onClick={() => setActiveDecision(null)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </form>
                ) : (
                  <div className="mt-5 flex flex-wrap gap-2">
                    <Button
                      onClick={() =>
                        setActiveDecision({ id: item.id, action: "approve" })
                      }
                      disabled={busy}
                    >
                      Approve
                    </Button>
                    <Button
                      onClick={() =>
                        setActiveDecision({ id: item.id, action: "reject" })
                      }
                      disabled={busy}
                      variant="secondary"
                    >
                      Reject
                    </Button>
                    <Button
                      onClick={() =>
                        setActiveDecision({ id: item.id, action: "edit" })
                      }
                      disabled={busy}
                      variant="secondary"
                    >
                      Edit
                    </Button>
                    <Button
                      onClick={() =>
                        setActiveDecision({ id: item.id, action: "regenerate" })
                      }
                      disabled={busy}
                      variant="secondary"
                    >
                      Regenerate
                    </Button>
                  </div>
                )
              ) : (
                <p className="mt-4 text-sm text-[#aaa]">
                  {item.decision_comment}
                </p>
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
