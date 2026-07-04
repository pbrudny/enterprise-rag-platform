import axios from "axios";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AuditEventsTable } from "../components/AuditEventsTable";
import { useUser } from "../context/UserContext";
import { getDocumentActivity, postDocument } from "../services/documentsApi";
import type { AuditEvent } from "../types/audit";
import type { DocumentIngestResponse } from "../types/document";

const CLASSIFICATION_LEVELS = ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"];
const INGEST_ROLES = new Set(["manager", "security_admin"]);

export function DocumentsPage() {
  const { selectedUser } = useUser();
  const [file, setFile] = useState<File | null>(null);
  const [aclGroup, setAclGroup] = useState<string>("all");
  const [classification, setClassification] = useState<string>("INTERNAL");
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState<DocumentIngestResponse | null>(null);
  const [quarantine, setQuarantine] = useState<string[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activity, setActivity] = useState<AuditEvent[]>([]);

  const canIngest = !!selectedUser && INGEST_ROLES.has(selectedUser.role);
  const allowedClassifications = selectedUser
    ? CLASSIFICATION_LEVELS.slice(0, CLASSIFICATION_LEVELS.indexOf(selectedUser.clearance) + 1)
    : [];
  const allowedAclGroups = selectedUser ? [...selectedUser.acl_groups, "all"] : [];

  useEffect(() => {
    if (!canIngest || !selectedUser) return;
    getDocumentActivity(selectedUser.user_id).then(setActivity).catch(() => {});
  }, [canIngest, selectedUser]);

  if (!selectedUser) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <p className="text-sm text-slate-600">
          No user selected. <Link to="/" className="underline">Pick one first.</Link>
        </p>
      </div>
    );
  }

  if (!canIngest) {
    return (
      <div className="mx-auto max-w-3xl p-6">
        <p className="text-sm text-slate-600">
          {selectedUser.display_name} has role <span className="font-medium">{selectedUser.role}</span>
          , which cannot ingest documents. Only managers and security admins can — pick a
          different <Link to="/" className="underline">user</Link>.
        </p>
      </div>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !selectedUser) return;

    setSubmitting(true);
    setSuccess(null);
    setQuarantine(null);
    setError(null);

    const formData = new FormData();
    formData.append("user_id", selectedUser.user_id);
    formData.append("acl_group", aclGroup);
    formData.append("classification", classification);
    formData.append("file", file);

    try {
      const response = await postDocument(formData);
      setSuccess(response);
      setFile(null);
      getDocumentActivity(selectedUser.user_id).then(setActivity).catch(() => {});
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 422) {
        setQuarantine(err.response.data.detail.matched_patterns ?? []);
      } else if (axios.isAxiosError(err) && typeof err.response?.data?.detail === "string") {
        setError(err.response.data.detail);
      } else {
        setError("Upload failed. Is the API running (uv run rag serve)?");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Ingest a document</h1>
        <p className="mt-1 text-sm text-slate-500">
          As <span className="font-medium text-slate-900">{selectedUser.display_name}</span> (
          {selectedUser.tenant_id}) — documents are always attributed to your own tenant; you
          can't ingest for another tenant, above your own clearance ({selectedUser.clearance}), or
          into an ACL group you don't belong to.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-slate-200 p-4">
        <div>
          <label htmlFor="doc-file" className="block text-sm font-medium text-slate-700">
            File (.md, .txt, .pdf)
          </label>
          <input
            id="doc-file"
            type="file"
            accept=".md,.txt,.pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="mt-1 block w-full text-sm"
          />
        </div>

        <div className="flex gap-4">
          <div className="flex-1">
            <label htmlFor="doc-acl-group" className="block text-sm font-medium text-slate-700">
              ACL group
            </label>
            <select
              id="doc-acl-group"
              value={aclGroup}
              onChange={(e) => setAclGroup(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            >
              {allowedAclGroups.map((group) => (
                <option key={group} value={group}>
                  {group}
                </option>
              ))}
            </select>
          </div>

          <div className="flex-1">
            <label htmlFor="doc-classification" className="block text-sm font-medium text-slate-700">
              Classification
            </label>
            <select
              id="doc-classification"
              value={classification}
              onChange={(e) => setClassification(e.target.value)}
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            >
              {allowedClassifications.map((level) => (
                <option key={level} value={level}>
                  {level}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={!file || submitting}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {submitting ? "Ingesting..." : "Ingest"}
        </button>
      </form>

      {success && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-800">
          Ingested <span className="font-mono">{success.doc_id}</span> ({success.title})
        </div>
      )}

      {quarantine && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-800">
          <p className="font-medium">Quarantined: matched prompt-injection patterns</p>
          <ul className="mt-1 list-inside list-disc font-mono text-xs">
            {quarantine.map((pattern) => (
              <li key={pattern}>{pattern}</li>
            ))}
          </ul>
        </div>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-900">
          Recent activity for {selectedUser.tenant_id}
        </h3>
        <AuditEventsTable events={activity} />
      </div>
    </div>
  );
}
