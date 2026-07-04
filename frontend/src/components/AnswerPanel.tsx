interface Props {
  answer: string;
  citations: string[];
  sufficientContext: boolean;
}

export function AnswerPanel({ answer, citations, sufficientContext }: Props) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <h3 className="text-sm font-semibold text-slate-900">Answer</h3>
      <p className="mt-2 text-sm text-slate-800">{answer}</p>
      <p className="mt-2 text-xs text-slate-500">
        Citations: {citations.length > 0 ? citations.join(", ") : "(none)"}
      </p>
      {!sufficientContext && (
        <p className="mt-1 text-xs font-medium text-amber-700">
          Model flagged insufficient context.
        </p>
      )}
    </div>
  );
}
