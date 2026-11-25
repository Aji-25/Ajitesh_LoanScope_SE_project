import { useEffect, useRef, useState } from "react";

const words =
  "Every requirement keeps its source. Every decision keeps its evidence. Every change stays visible.".split(
    " ",
  );

export function TaglineReveal() {
  const containerRef = useRef<HTMLHeadingElement>(null);
  const [visibleWords, setVisibleWords] = useState<Set<number>>(new Set());

  useEffect(() => {
    const elements = containerRef.current?.querySelectorAll("span");
    if (!elements) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const index = Number((entry.target as HTMLElement).dataset.index);
          setVisibleWords((current) => new Set(current).add(index));
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "-35% 0px -35% 0px", threshold: 0.5 },
    );

    elements.forEach((element) => observer.observe(element));
    return () => observer.disconnect();
  }, []);

  return (
    <h2
      ref={containerRef}
      className="max-w-[680px] text-balance text-4xl font-semibold leading-tight sm:text-5xl lg:text-6xl"
    >
      {words.map((word, index) => (
        <span
          className={`mr-3 inline-block transition-all duration-700 ease-[cubic-bezier(0.32,0.72,0,1)] ${
            visibleWords.has(index) ? "text-white" : "text-white/30"
          }`}
          data-index={index}
          key={`${word}-${index}`}
          style={{ transitionDelay: `${(index % 5) * 50}ms` }}
        >
          {word}
        </span>
      ))}
    </h2>
  );
}
