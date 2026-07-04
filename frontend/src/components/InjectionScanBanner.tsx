interface Props {
  detected: boolean;
  matchedPatterns: string[];
}

export function InjectionScanBanner({ detected, matchedPatterns }: Props) {
  if (!detected) {
    return (
      <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-800">
        Injection scan: clean
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-800">
      <p className="font-medium">Injection scan: SUSPICIOUS</p>
      <ul className="mt-1 list-inside list-disc font-mono text-xs">
        {matchedPatterns.map((pattern) => (
          <li key={pattern}>{pattern}</li>
        ))}
      </ul>
    </div>
  );
}
