import { AlertTriangle, ArrowDownRight, ArrowUpRight, LockKeyhole, ShieldCheck } from 'lucide-react';
import type { DashboardData } from '@/lib/types';
import { comparisonLabel } from '@/lib/utils';

export function RunInsights({ data }: { data: DashboardData }) {
  return (
    <section className="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
      <article className="rounded-2xl border border-[#d9e0da] bg-white p-5 dark:border-[#2c3c34] dark:bg-[#15211b]">
        <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-[#587064] dark:text-[#8fb9a4]"><ArrowUpRight size={15} /> Added</p>
        <p className="mt-3 text-3xl font-semibold tracking-[-0.04em]">{data.comparison.added.length}</p>
        <p className="mt-2 line-clamp-2 text-sm leading-6 text-[#68756d] dark:text-[#a7b6ae]">{data.comparison.added.map(comparisonLabel).join(' · ') || 'No new roles this run.'}</p>
      </article>
      <article className="rounded-2xl border border-[#d9e0da] bg-white p-5 dark:border-[#2c3c34] dark:bg-[#15211b]">
        <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-[#785f48] dark:text-[#c6a789]"><ArrowDownRight size={15} /> Dropped</p>
        <p className="mt-3 text-3xl font-semibold tracking-[-0.04em]">{data.comparison.dropped.length}</p>
        <p className="mt-2 line-clamp-2 text-sm leading-6 text-[#68756d] dark:text-[#a7b6ae]">{data.comparison.dropped.map(comparisonLabel).join(' · ') || 'No roles dropped.'}</p>
      </article>
      <article className="rounded-2xl border border-[#d9e0da] bg-white p-5 dark:border-[#2c3c34] dark:bg-[#15211b]">
        <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-[#6f654b] dark:text-[#c4b47f]"><AlertTriangle size={15} /> Search notes</p>
        <p className="mt-3 text-3xl font-semibold tracking-[-0.04em]">{data.issues.length}</p>
        <p className="mt-2 line-clamp-2 text-sm leading-6 text-[#68756d] dark:text-[#a7b6ae]">{data.issues[0] || 'No material search issues reported.'}</p>
      </article>
      <article className="rounded-2xl border border-[#d9e0da] bg-white p-5 dark:border-[#2c3c34] dark:bg-[#15211b]">
        <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.12em] text-[#55687a] dark:text-[#94aec5]"><LockKeyhole size={15} /> Login walls</p>
        <p className="mt-3 text-3xl font-semibold tracking-[-0.04em]">{data.blocked_sources.length}</p>
        <p className="mt-2 line-clamp-2 text-sm leading-6 text-[#68756d] dark:text-[#a7b6ae]">{data.blocked_sources.map((item) => item.site).join(', ') || 'All priority sources were accessible.'}</p>
      </article>
      <div className="sr-only"><ShieldCheck /> Live-listing checks are represented in the source data.</div>
    </section>
  );
}
