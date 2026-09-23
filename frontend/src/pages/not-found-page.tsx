import { ArrowLeft } from "@phosphor-icons/react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";

export function NotFoundPage() {
  return (
    <main className="grid min-h-screen place-items-center bg-[#131209] px-6 py-24">
      <section className="text-center">
        <p className="font-mono text-sm text-[#d9ff76]">404</p>
        <h1 className="mt-4 text-balance text-4xl font-semibold">This requirement is outside the current scope.</h1>
        <p className="mx-auto mt-4 max-w-md text-pretty text-base text-[#9b9b9b]">
          The page may have moved, or the workflow has not reached this stage yet.
        </p>
        <Button asChild className="mt-8">
          <Link to="/">
            <ArrowLeft aria-hidden="true" /> Return home
          </Link>
        </Button>
      </section>
    </main>
  );
}
