interface Props {
  passed: boolean;
  reason: string | null;
}

export function ValidationBanner({ passed, reason }: Props) {
  const style = passed
    ? "border-emerald-200 bg-emerald-50 text-emerald-800"
    : "border-amber-200 bg-amber-50 text-amber-800";

  return (
    <div className={`rounded-lg border px-4 py-2 text-sm ${style}`}>
      Output validation: {passed ? "passed" : reason}
    </div>
  );
}
