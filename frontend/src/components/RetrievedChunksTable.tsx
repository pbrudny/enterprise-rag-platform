import type { RetrievedChunkView } from "../types/query";

interface Props {
  chunks: RetrievedChunkView[];
}

export function RetrievedChunksTable({ chunks }: Props) {
  if (chunks.length === 0) {
    return <p className="text-sm text-slate-500">No chunks retrieved.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-left text-xs font-medium uppercase text-slate-500">
          <tr>
            <th className="px-3 py-2">Chunk ID</th>
            <th className="px-3 py-2">Tenant</th>
            <th className="px-3 py-2">ACL group</th>
            <th className="px-3 py-2">Classification</th>
            <th className="px-3 py-2">Score</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {chunks.map((chunk) => (
            <tr key={chunk.chunk_id}>
              <td className="px-3 py-2 font-mono text-xs text-slate-700">{chunk.chunk_id}</td>
              <td className="px-3 py-2 text-slate-600">{chunk.tenant_id}</td>
              <td className="px-3 py-2 text-slate-600">{chunk.acl_group}</td>
              <td className="px-3 py-2 text-slate-600">{chunk.classification}</td>
              <td className="px-3 py-2 text-slate-600">{chunk.score.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
