// frontend/src/components/contributors/ContributorTable.tsx

import { formatNumber, formatDate } from "@/lib/utils";
import type { ContributorStat } from "@/types";

export function ContributorTable({ contributors }: { contributors: ContributorStat[] }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-white/8">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/8 bg-surface-100">
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Contributor</th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">Commits</th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">PRs</th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">Issues</th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">Additions</th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">Deletions</th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">Last Active</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {contributors.map((c, i) => (
            <tr key={c.github_login} className="hover:bg-white/2 transition-colors">
              <td className="px-4 py-3">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-600 w-5 text-right">{i + 1}</span>
                  {c.avatar_url && (
                    <img src={c.avatar_url} alt={c.github_login} className="h-7 w-7 rounded-full" />
                  )}
                  
                    href={`https://github.com/${c.github_login}`}
                    target="_blank"
                    rel="noreferrer"
                    className="font-medium text-slate-200 hover:text-brand-400 transition-colors"
                  >
                    {c.github_login}
                  </a>
                </div>
              </td>
              <td className="px-4 py-3 text-right font-mono text-slate-300">{formatNumber(c.commit_count)}</td>
              <td className="px-4 py-3 text-right font-mono text-slate-300">{formatNumber(c.pr_count)}</td>
              <td className="px-4 py-3 text-right font-mono text-slate-300">{formatNumber(c.issue_count)}</td>
              <td className="px-4 py-3 text-right font-mono text-emerald-500">+{formatNumber(c.total_additions)}</td>
              <td className="px-4 py-3 text-right font-mono text-red-500">-{formatNumber(c.total_deletions)}</td>
              <td className="px-4 py-3 text-right text-slate-600">{formatDate(c.last_commit_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}