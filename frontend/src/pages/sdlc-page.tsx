import { ChartBar, Sparkle, SpinnerGap, WarningCircle } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { ApiError, apiRequest } from "@/api/client";
import type { SDLCRecommendation, SDLCSuggestion } from "@/api/types";
import type { ProjectOutletContext } from "@/components/project-layout";
import { Button } from "@/components/ui/button";

const fields = [
  ["requirements_volatility", "Requirements volatility"],
  ["compliance_criticality", "Compliance criticality"],
  ["technical_risk", "Technical risk"],
  ["customer_collaboration", "Customer collaboration"],
  ["release_frequency", "Release frequency"],
  ["team_experience", "Team experience"],
] as const;
const modelLabels: Record<string, string> = {
  waterfall: "Waterfall model",
  v_shaped: "V-shaped",
  spiral: "Spiral",
  prototype: "Prototype",
  rapid_application_development: "Rapid application development (RAD)",
  iterative_incremental: "Iterative/incremental",
  agile: "Agile",
};

function ScoreBreakdown({ scores }: { scores: Record<string, number> }) {
  return (
    <ul className="mt-4 space-y-3">
      {Object.entries(scores).sort((a, b) => b[1] - a[1]).map(([name, score]) => (
        <li key={name}>
          <div className="flex justify-between gap-3 text-sm">
            <span>{modelLabels[name] ?? name}</span>
            <span>{score}%</span>
          </div>
          <div className="mt-1 h-2 rounded-full bg-[#111]" aria-hidden="true">
            <div className="h-full rounded-full bg-[#d9ff76]" style={{ width: `${score}%` }} />
          </div>
        </li>
      ))}
    </ul>
  );
}

export function SDLCPage() {
  const { project } = useOutletContext<ProjectOutletContext>();
  const path = `/projects/${project.id}/sdlc`;
  const [values, setValues] = useState<Record<string, number>>(
    () => Object.fromEntries(fields.map(([key]) => [key, 3])),
  );
  const [result, setResult] = useState<SDLCRecommendation | null>(null);
  const [busy, setBusy] = useState(false);
  const [suggesting, setSuggesting] = useState(false);
  const [suggestion, setSuggestion] = useState<SDLCSuggestion | null>(null);
  const [error, setError] = useState("");
  const [aiError, setAiError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    apiRequest<SDLCRecommendation>(`${path}/latest`, {
      authenticated: true,
      signal: controller.signal,
    })
      .then((latest) => {
        setResult(latest);
        setValues(latest.characteristics);
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted && (!(reason instanceof ApiError) || reason.status !== 404)) {
          setError(reason instanceof Error ? reason.message : "Could not load the recommendation.");
        }
      });
    return () => controller.abort();
  }, [path]);

  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setSuggesting(true);
    setAiError("");
    setSuggestion(null);
    apiRequest<SDLCSuggestion>(`${path}/suggest`, {
      method: "POST",
      authenticated: true,
      signal: controller.signal,
    })
      .then(setSuggestion)
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) setAiError(reason instanceof Error ? reason.message : "Could not get an AI recommendation.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setSuggesting(false);
      });
    return () => controller.abort();
  }, [path, retry]);

  async function calculate(inputs = values, fromAI = false) {
    setBusy(true);
    setError("");
    try {
      setResult(await apiRequest<SDLCRecommendation>(`${path}/recommend`, {
        method: "POST",
        authenticated: true,
        body: JSON.stringify(inputs),
      }));
      if (fromAI) setValues(inputs);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Scoring failed.");
    } finally {
      setBusy(false);
    }
  }

  const scoresAreOutdated = result && fields.some(([key]) => result.characteristics[key] !== values[key]);
  const aiSaved = suggestion && result && fields.every(([key]) => suggestion.characteristics[key] === result.characteristics[key]);
  return (
    <div>
      <h1 className="text-4xl font-semibold">SDLC recommendation</h1>
      <section aria-labelledby="ai-sdlc-title" className="mt-8 rounded-2xl border border-[#d9ff76]/20 bg-[#181818] p-6 sm:p-8">
        <h2 id="ai-sdlc-title" className="flex items-center gap-2 text-lg font-semibold"><Sparkle aria-hidden="true" className="text-[#d9ff76]" />AI recommendation</h2>
        {suggesting && (
          <p role="status" className="mt-5 flex items-center gap-2 text-sm text-[#bcbcbc]">
            <SpinnerGap aria-hidden="true" className="animate-spin" /> Reading your project and requirements…
          </p>
        )}
        {aiError && (
          <div className="mt-5">
            <p role="alert" className="text-sm text-red-200">{aiError}</p>
            <Button onClick={() => setRetry((current) => current + 1)} variant="secondary" className="mt-3">Retry AI recommendation</Button>
          </div>
        )}
        {suggestion && (
          <div className="mt-4">
            <div className="flex flex-wrap items-baseline gap-x-4 gap-y-2">
              <p className="text-4xl font-semibold text-[#d9ff76]">{modelLabels[suggestion.preview.recommendation] ?? suggestion.preview.recommendation}</p>
              <p className="text-lg font-semibold text-[#e1e1e1]">{suggestion.preview.scores[suggestion.preview.recommendation]}% fit</p>
            </div>
            <p className="mt-2 max-w-3xl text-sm text-[#bcbcbc]">{suggestion.rationale}</p>
            <div className="mt-6 grid gap-6 lg:grid-cols-2">
              <div>
                <h3 className="font-semibold">AI ratings</h3>
                <dl className="mt-2 divide-y divide-white/10 text-sm">
                  {fields.map(([key, label]) => (
                    <div key={key} className="flex items-center justify-between gap-3 py-2">
                      <dt>{label}{suggestion.assumptions.includes(key) && <span className="ml-2 text-xs text-amber-200">Provisional</span>}</dt>
                      <dd className="shrink-0 font-medium">{suggestion.characteristics[key]}/5</dd>
                    </div>
                  ))}
                </dl>
              </div>
              <div>
                <h3 className="font-semibold">Compare delivery models</h3>
                <ScoreBreakdown scores={suggestion.preview.scores} />
              </div>
            </div>
            <Button className="mt-6" variant="secondary" disabled={busy || !!aiSaved} onClick={() => void calculate(suggestion.characteristics, true)}>
              {aiSaved ? "Recommendation saved" : "Save AI recommendation"}
            </Button>
          </div>
        )}
      </section>
      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-white/10 bg-[#181818] p-6">
          <h2 className="text-xl font-semibold">Manual project characteristics</h2>
          <div className="mt-5 space-y-5">
            {fields.map(([key, label]) => (
              <label key={key} className="block text-sm">
                <span className="flex justify-between gap-3">
                  <span>{label}</span>
                  <span aria-hidden="true" className="text-[#d9ff76]">{values[key]}</span>
                </span>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={values[key]}
                  onChange={(event) =>
                    setValues((current) => ({ ...current, [key]: Number(event.target.value) }))
                  }
                  className="mt-2 w-full accent-[#d9ff76]"
                />
              </label>
            ))}
          </div>
          <Button onClick={() => void calculate()} disabled={busy} className="mt-6 w-full">
            {busy ? <SpinnerGap aria-hidden="true" className="animate-spin" /> : <ChartBar aria-hidden="true" />}
            Calculate manual scores
          </Button>
          {error && <p role="alert" className="mt-4 flex gap-2 text-red-200"><WarningCircle aria-hidden="true" />{error}</p>}
        </section>
        <section className="rounded-2xl border border-white/10 bg-[#181818] p-6">
          <h2 className="text-xl font-semibold">Saved score breakdown</h2>
          {scoresAreOutdated && <p className="mt-3 text-sm text-amber-200">Inputs changed. Calculate scores to update this ranking.</p>}
          {result ? (
            <div className="mt-4">
              <p className="text-sm text-[#bcbcbc]">Recommended model</p>
              <p className="mt-1 text-2xl font-semibold text-[#d9ff76]">{modelLabels[result.recommendation] ?? result.recommendation}</p>
              <ScoreBreakdown scores={result.scores} />
              <p className="mt-5 text-xs text-[#bcbcbc]">Scoring model {result.scoring_version}</p>
            </div>
          ) : <p className="mt-4 text-[#bcbcbc]">Calculate to compare delivery approaches.</p>}
        </section>
      </div>


    </div>
  );
}
