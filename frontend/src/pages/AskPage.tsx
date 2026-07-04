import { useState } from "react";
import { Link } from "react-router-dom";
import { AccessContextPanel } from "../components/AccessContextPanel";
import { AnswerPanel } from "../components/AnswerPanel";
import { InjectionScanBanner } from "../components/InjectionScanBanner";
import { RetrievedChunksTable } from "../components/RetrievedChunksTable";
import { ValidationBanner } from "../components/ValidationBanner";
import { useUser } from "../context/UserContext";
import { postQuery } from "../services/queryApi";
import type { QueryResponse } from "../types/query";

export function AskPage() {
  const { selectedUser } = useUser();
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!selectedUser) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <p className="text-sm text-slate-600">
          No user selected. <Link to="/" className="underline">Pick one first.</Link>
        </p>
      </div>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || !selectedUser) return;

    setLoading(true);
    setError(null);
    try {
      const response = await postQuery({ user_id: selectedUser.user_id, question });
      setResult(response);
    } catch {
      setError("Query failed. Is the API running (uv run rag serve)?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-4 p-6">
      <h1 className="text-xl font-semibold text-slate-900">Ask a question</h1>
      <p className="text-sm text-slate-500">
        Asking as <span className="font-medium text-slate-900">{selectedUser.display_name}</span> (
        {selectedUser.tenant_id})
      </p>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What is our VPN password rotation policy?"
          className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "Asking..." : "Ask"}
        </button>
      </form>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {result && (
        <div className="space-y-4">
          <AccessContextPanel
            accessContext={result.access_context}
            filterApplied={result.filter_applied}
          />
          <InjectionScanBanner
            detected={result.injection_detected}
            matchedPatterns={result.injection_matched_patterns}
          />
          <div>
            <h3 className="mb-2 text-sm font-semibold text-slate-900">Retrieved chunks</h3>
            <RetrievedChunksTable chunks={result.chunks} />
          </div>
          <ValidationBanner passed={result.validation_passed} reason={result.validation_reason} />
          <AnswerPanel
            answer={result.answer}
            citations={result.citations}
            sufficientContext={result.sufficient_context}
          />
        </div>
      )}
    </div>
  );
}
