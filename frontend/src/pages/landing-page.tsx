import {
  ArrowRight,
  Check,
  ClipboardText,
  FileMagnifyingGlass,
  Fingerprint,
  Quotes,
  ShieldCheck,
} from "@phosphor-icons/react";
import { Link } from "react-router-dom";

import { ApiStatusCard } from "@/components/api-status-card";
import { Navigation } from "@/components/navigation";
import { Reveal } from "@/components/reveal";
import { TaglineReveal } from "@/components/tagline-reveal";
import { Button } from "@/components/ui/button";

const benefits = [
  {
    icon: ClipboardText,
    title: "Structured discovery",
    body: "Turn each stakeholder answer into a requirement with source, priority, assumptions, and acceptance criteria.",
  },
  {
    icon: FileMagnifyingGlass,
    title: "Grounded compliance",
    body: "Connect compliance findings to approved source passages instead of relying on unsupported interpretation.",
  },
  {
    icon: ShieldCheck,
    title: "Visible review",
    body: "Route high impact requirements and risk decisions to the right human reviewer before they become a baseline.",
  },
  {
    icon: Fingerprint,
    title: "Explainable planning",
    body: "Score delivery models with deterministic rules and keep the reasoning available for project review.",
  },
];

const faqs = [
  {
    question: "Is LoanScope a loan decisioning system?",
    answer:
      "No. LoanScope supports requirement engineering for personal loan software projects. It does not approve borrowers, access live credit data, or move money.",
  },
  {
    question: "How are compliance findings supported?",
    answer:
      "The planned compliance workflow retrieves relevant passages from an approved document library and stores the source reference beside each mapping.",
  },
  {
    question: "Can a person change an extracted requirement?",
    answer:
      "Yes. Human review is central to the workflow. Reviewers can edit, reject, approve, or request a revision before important decisions are finalized.",
  },
  {
    question: "Where is project data stored?",
    answer:
      "Application records and retrieval metadata use PostgreSQL. Vector search uses pgvector in the same database to keep the architecture understandable.",
  },
  {
    question: "Who is the workspace designed for?",
    answer:
      "Business analysts, lending stakeholders, compliance officers, security reviewers, and project managers can each review the parts relevant to their role.",
  },
  {
    question: "Does the system choose an SDLC by itself?",
    answer:
      "No. Deterministic rules rank suitable models, a language model explains those scores, and a human approves the final recommendation.",
  },
];

export function LandingPage() {
  return (
    <div className="min-h-screen overflow-hidden bg-[#131209]">
      <a
        className="fixed left-4 top-4 z-50 -translate-y-20 rounded-lg bg-[#d9ff76] px-3 py-2 text-sm font-semibold text-[#131209] transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] focus:translate-y-0"
        href="#main-content"
      >
        Skip to content
      </a>
      <Navigation />

      <main id="main-content">
        <section className="mx-auto grid min-h-screen max-w-7xl items-center gap-12 px-6 pb-20 pt-36 lg:grid-cols-[1.05fr_0.95fr] lg:px-8">
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-[#181818] px-3 py-2 text-sm font-semibold text-[#c8c8c8]">
              <span className="size-2 rounded-full bg-[#d9ff76]" />
              Built for personal loan delivery teams
            </div>
            <h1 className="max-w-[680px] bg-gradient-to-r from-white to-[#9b9b9b] bg-clip-text text-balance text-5xl font-semibold leading-none text-transparent sm:text-6xl lg:text-7xl">
              Turn lending conversations into requirements your team can defend.
            </h1>
            <p className="mt-6 max-w-[680px] text-pretty text-lg text-[#b6b6b6] sm:text-xl">
              LoanScope guides discovery, preserves source evidence, and turns reviewed requirements into an explainable delivery plan.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Button asChild>
                <Link to="/projects/new">
                  Start a project <ArrowRight aria-hidden="true" weight="bold" />
                </Link>
              </Button>
              <Button asChild variant="secondary">
                <a href="#workflow">See the workflow</a>
              </Button>
            </div>
            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-sm text-[#9b9b9b]">
              {[
                "Versioned requirements",
                "Traceable source evidence",
                "Deterministic SDLC scoring",
              ].map((item) => (
                <span className="flex items-center gap-2" key={item}>
                  <Check aria-hidden="true" className="text-[#d9ff76]" weight="bold" /> {item}
                </span>
              ))}
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-8 rounded-full bg-[#d9ff76]/5 blur-3xl" />
            <div className="relative rounded-2xl border border-white/10 bg-[#181818] p-3 shadow-2xl shadow-black/50 sm:p-4">
              <div className="rounded-xl bg-[#1f1f1f] p-4 sm:p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-[#9b9b9b]">Riverstone lending portal</p>
                    <h2 className="mt-1 text-xl font-semibold">Requirement review</h2>
                  </div>
                  <span className="rounded-full bg-[#d9ff76]/10 px-3 py-1 text-xs font-semibold text-[#d9ff76]">
                    Discovery
                  </span>
                </div>
                <div className="mt-6 space-y-3">
                  <div className="rounded-xl border border-white/10 bg-[#181818] p-4">
                    <div className="flex items-start gap-3">
                      <span className="rounded-md bg-[#d9ff76] px-2 py-1 font-mono text-xs font-bold text-[#131209]">
                        FR 012
                      </span>
                      <div>
                        <p className="text-pretty text-sm font-semibold">
                          Loan officers can review identity documents before submitting an application for credit assessment.
                        </p>
                        <p className="mt-2 text-xs text-[#9b9b9b]">Source: Meera Nair, lending operations</p>
                      </div>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <span className="rounded-full bg-[#272727] px-3 py-1 text-xs text-[#c8c8c8]">Functional</span>
                      <span className="rounded-full bg-[#272727] px-3 py-1 text-xs text-[#c8c8c8]">Identity review</span>
                      <span className="rounded-full bg-[#d9ff76]/10 px-3 py-1 text-xs text-[#d9ff76]">Ready to validate</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      ["24", "Requirements"],
                      ["3", "Open questions"],
                      ["5", "Policy sources"],
                    ].map(([value, label]) => (
                      <div className="rounded-xl bg-[#272727] p-3" key={label}>
                        <p className="text-lg font-semibold">{value}</p>
                        <p className="text-pretty text-xs text-[#9b9b9b]">{label}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="mt-3">
                <ApiStatusCard />
              </div>
            </div>
          </div>
        </section>

        <section className="border-y border-white/10 bg-[#181818] px-6 py-24 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <TaglineReveal />
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-6 py-24 lg:px-8" id="benefits">
          <Reveal>
            <p className="text-sm font-semibold text-[#d9ff76]">A reliable project record</p>
            <h2 className="mt-3 max-w-[680px] text-balance text-3xl font-semibold sm:text-4xl">
              Keep semantic analysis connected to accountable decisions.
            </h2>
          </Reveal>
          <div className="mt-12 grid gap-4 md:grid-cols-2">
            {benefits.map(({ icon: Icon, title, body }) => (
              <Reveal className="h-full" key={title}>
                <article className="h-full rounded-2xl border border-white/10 bg-[#181818] p-6 transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] hover:-translate-y-1 hover:border-white/20">
                  <span className="grid size-12 place-items-center rounded-lg bg-[#272727] text-[#d9ff76]">
                    <Icon aria-hidden="true" size={24} />
                  </span>
                  <h3 className="mt-6 text-xl font-semibold">{title}</h3>
                  <p className="mt-3 max-w-lg text-pretty text-base text-[#9b9b9b]">{body}</p>
                </article>
              </Reveal>
            ))}
          </div>
        </section>

        <section className="bg-[#181818] px-6 py-24 lg:px-8" id="workflow">
          <div className="mx-auto max-w-7xl">
            <Reveal>
              <p className="text-sm font-semibold text-[#d9ff76]">Three deliberate stages</p>
              <h2 className="mt-3 max-w-[680px] text-balance text-3xl font-semibold sm:text-4xl">
                Move from open conversation to an approved delivery direction.
              </h2>
            </Reveal>
            <div className="mt-12 grid gap-4 lg:grid-cols-3">
              {[
                ["01", "Capture context", "A guided interview asks one relevant question at a time and preserves who supplied each answer."],
                ["02", "Review requirements", "Structured candidates surface ambiguity, conflict, security concerns, and evidence gaps for review."],
                ["03", "Approve the plan", "Deterministic scoring ranks delivery approaches before a project manager approves the recommendation."],
              ].map(([number, title, body]) => (
                <Reveal key={number}>
                  <article className="rounded-2xl border border-white/10 bg-[#1f1f1f] p-6">
                    <span className="font-mono text-sm text-[#d9ff76]">{number}</span>
                    <h3 className="mt-8 text-xl font-semibold">{title}</h3>
                    <p className="mt-3 text-pretty text-base text-[#9b9b9b]">{body}</p>
                  </article>
                </Reveal>
              ))}
            </div>
            <Reveal className="mt-12">
              <figure className="rounded-2xl border border-white/10 bg-[#1f1f1f] p-6 sm:p-8">
                <Quotes aria-hidden="true" className="text-[#d9ff76]" size={32} weight="fill" />
                <blockquote className="mt-6 max-w-3xl text-balance text-2xl font-medium text-white">
                  The system is designed to show why a requirement exists, what evidence supports it, and who approved the decision.
                </blockquote>
                <figcaption className="mt-6 text-sm text-[#9b9b9b]">Core project principle</figcaption>
              </figure>
            </Reveal>
          </div>
        </section>

        <section className="mx-auto max-w-4xl px-6 py-24" id="questions">
          <Reveal>
            <p className="text-center text-sm font-semibold text-[#d9ff76]">Common questions</p>
            <h2 className="mt-3 text-balance text-center text-3xl font-semibold sm:text-4xl">
              Clear boundaries from the beginning.
            </h2>
          </Reveal>
          <div className="mt-12 space-y-3">
            {faqs.map(({ question, answer }) => (
              <details className="group rounded-xl border border-white/10 bg-[#181818] p-6" key={question}>
                <summary className="cursor-pointer list-none pr-8 text-base font-semibold marker:hidden">
                  {question}
                </summary>
                <p className="mt-4 max-w-3xl text-pretty text-sm text-[#9b9b9b]">{answer}</p>
              </details>
            ))}
          </div>
        </section>

        <section className="px-6 pb-24 lg:px-8">
          <Reveal className="mx-auto max-w-7xl rounded-2xl border border-white/10 bg-[#d9ff76] px-6 py-16 text-center text-[#131209] sm:px-12">
            <h2 className="mx-auto max-w-[680px] text-balance text-3xl font-semibold sm:text-4xl">
              Build a requirement baseline your whole delivery team can inspect.
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-pretty text-base text-[#3c421e]">
              Start with a project brief. LoanScope will guide the rest of the discovery process as each workflow phase becomes available.
            </p>
            <Button asChild className="mt-8 bg-[#131209] text-white hover:bg-[#272727]">
              <Link to="/projects/new">Start a project</Link>
            </Button>
          </Reveal>
        </section>
      </main>

      <footer className="border-t border-white/10 px-6 py-8 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 text-sm text-[#9b9b9b] sm:flex-row sm:items-center sm:justify-between">
          <p>LoanScope supports requirement engineering for personal loan software projects.</p>
          <nav aria-label="Legal navigation" className="flex gap-4">
            <Link className="rounded-md hover:text-white" to="/privacy">Privacy</Link>
            <Link className="rounded-md hover:text-white" to="/terms">Terms</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
