import { ArrowRight, List, X } from "@phosphor-icons/react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";

const links = [
  { label: "Benefits", href: "#benefits" },
  { label: "Workflow", href: "#workflow" },
  { label: "Questions", href: "#questions" },
];

export function Navigation() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <nav
        aria-label="Main navigation"
        className="fixed left-1/2 top-0 z-40 mt-6 flex w-[calc(100%-2rem)] max-w-4xl -translate-x-1/2 items-center justify-between rounded-full border border-white/10 bg-[#181818]/90 px-4 py-2 shadow-2xl shadow-black/30 backdrop-blur-3xl sm:px-6"
      >
        <Link
          aria-label="Clarifi home"
          className="flex items-center gap-2 rounded-full text-base font-semibold"
          to="/"
        >
          <span className="grid size-8 place-items-center rounded-full bg-[#d9ff76] text-sm font-bold text-[#131209]">
            C
          </span>
          Clarifi
        </Link>
        <div className="hidden items-center gap-1 md:flex">
          {links.map((link) => (
            <a
              className="rounded-full px-3 py-2 text-sm font-semibold text-[#b6b6b6] transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] hover:bg-[#272727] hover:text-white active:scale-[0.98]"
              href={link.href}
              key={link.href}
            >
              {link.label}
            </a>
          ))}
        </div>
        <Button asChild className="hidden md:inline-flex" size="small">
          <Link to="/projects/new">
            Start a project <ArrowRight aria-hidden="true" weight="bold" />
          </Link>
        </Button>
        <button
          aria-expanded={open}
          aria-label={open ? "Close navigation" : "Open navigation"}
          className="relative grid size-9 place-items-center rounded-full text-white transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] hover:bg-[#272727] active:scale-[0.98] md:hidden"
          onClick={() => setOpen((value) => !value)}
          type="button"
        >
          <List
            aria-hidden="true"
            className={`absolute transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] ${open ? "rotate-45 opacity-0" : "rotate-0 opacity-100"}`}
            size={22}
          />
          <X
            aria-hidden="true"
            className={`absolute transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] ${open ? "rotate-0 opacity-100" : "-rotate-45 opacity-0"}`}
            size={22}
          />
        </button>
      </nav>
      <div
        aria-hidden={!open}
        className={`fixed inset-0 z-30 bg-black/80 px-6 pt-32 backdrop-blur-3xl transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] md:hidden ${
          open ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"
        }`}
      >
        <div className="mx-auto flex max-w-md flex-col gap-3">
          {links.map((link, index) => (
            <a
              className={`rounded-xl px-4 py-3 text-2xl font-semibold transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] hover:bg-[#272727] ${
                open ? "translate-y-0 opacity-100" : "translate-y-12 opacity-0"
              }`}
              href={link.href}
              key={link.href}
              onClick={() => setOpen(false)}
              style={{ transitionDelay: `${100 + index * 50}ms` }}
            >
              {link.label}
            </a>
          ))}
          <Button asChild className="mt-3">
            <Link to="/projects/new">Start a project</Link>
          </Button>
        </div>
      </div>
    </>
  );
}
