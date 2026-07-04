import mermaid from "mermaid";
import { useEffect, useId, useRef } from "react";

mermaid.initialize({ startOnLoad: false, theme: "neutral", securityLevel: "strict" });

interface Props {
  chart: string;
}

export function MermaidDiagram({ chart }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const id = useId().replace(/:/g, "-");

  useEffect(() => {
    let cancelled = false;

    mermaid.render(`mermaid-${id}`, chart).then(({ svg }) => {
      if (!cancelled && ref.current) {
        ref.current.innerHTML = svg;
      }
    });

    return () => {
      cancelled = true;
    };
  }, [chart, id]);

  return <div ref={ref} className="overflow-x-auto" />;
}
