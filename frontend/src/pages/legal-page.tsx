import { ArrowLeft } from "@phosphor-icons/react";
import { Link } from "react-router-dom";

type LegalPageProps = { title: "Privacy" | "Terms" };

export function LegalPage({ title }: LegalPageProps) {
  return (
    <main className="min-h-screen bg-[#131209] px-6 py-24">
      <article className="mx-auto max-w-2xl">
        <Link className="inline-flex items-center gap-2 rounded-md text-sm font-semibold text-[#d9ff76]" to="/">
          <ArrowLeft aria-hidden="true" /> Back to Clarifi
        </Link>
        <h1 className="mt-12 text-4xl font-semibold">{title}</h1>
        <p className="mt-6 text-pretty text-base text-[#b6b6b6]">
          This development preview does not accept account details or production lending data. A complete {title.toLowerCase()} notice will be published before stakeholder information is collected.
        </p>
      </article>
    </main>
  );
}
