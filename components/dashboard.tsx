'use client';

import { useEffect, useMemo } from 'react';
import { BriefcaseBusiness, Check, Clipboard, CloudOff, Download, RefreshCw, Sparkles } from 'lucide-react';
import { Filters } from '@/components/filters';
import { JobCard } from '@/components/job-card';
import { RunInsights } from '@/components/run-insights';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogTitle } from '@/components/ui/dialog';
import { useJobStore } from '@/store/use-job-store';
import { formatDate } from '@/lib/utils';

export function Dashboard() {
  const {
    data,
    filters,
    loading,
    mutatingJobId,
    backendAvailable,
    notice,
    coverLetter,
    coverLetterOpen,
    load,
    setFilter,
    clearFilters,
    updateStatus,
    generateCoverLetter,
    setCoverLetterOpen,
  } = useJobStore();

  useEffect(() => { void load(); }, [load]);

  const visibleJobs = useMemo(() => {
    const query = filters.query.trim().toLowerCase();
    const filtered = data.jobs.filter((job) => {
      const haystack = [job.role, job.company, job.location, job.strategic_note, job.suggested_resume].filter(Boolean).join(' ').toLowerCase();
      return (!query || haystack.includes(query))
        && job.score >= filters.minScore
        && (!filters.company || job.company === filters.company)
        && (!filters.location || job.location === filters.location)
        && (filters.status === 'all' || job.status === filters.status);
    });
    return filtered.sort((a, b) => {
      if (filters.sort === 'company_asc') return a.company.localeCompare(b.company);
      if (filters.sort === 'role_asc') return a.role.localeCompare(b.role);
      if (filters.sort === 'date_desc') return (b.posted || '').localeCompare(a.posted || '');
      return b.score - a.score;
    });
  }, [data.jobs, filters]);

  const copyLetter = async () => {
    if (coverLetter) await navigator.clipboard.writeText(coverLetter.content);
  };

  const downloadLetter = () => {
    if (!coverLetter) return;
    const url = URL.createObjectURL(new Blob([coverLetter.content], { type: 'text/plain' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = coverLetter.filename;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <main className="min-h-screen bg-[#f5f7f4] text-[#18231e]">
      <header className="sticky top-0 z-40 border-b border-[#dce2dd] bg-[#f5f7f4]/92 backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1580px] items-center justify-between gap-4 px-5 py-4 lg:px-8">
          <div className="flex items-center gap-3">
            <span className="grid size-10 place-items-center rounded-xl bg-[#183f31] text-white shadow-[0_8px_20px_rgba(24,63,49,0.18)]"><BriefcaseBusiness size={19} /></span>
            <div>
              <p className="font-semibold tracking-[-0.025em]">Role Radar</p>
              <p className="text-[11px] text-[#6e7b73]">Job search command center</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="hidden items-center gap-2 rounded-full border border-[#d7ded8] bg-white px-3 py-2 text-xs text-[#56645c] md:flex">
              <span className={`size-2 rounded-full ${backendAvailable ? 'bg-[#42a675]' : 'bg-[#e0a43a]'}`} />
              {backendAvailable ? 'Live workspace' : 'Preview mode'}
            </span>
            <Button variant="secondary" size="sm" onClick={() => void load()} disabled={loading}>
              <RefreshCw className={loading ? 'animate-spin' : ''} size={14} /> <span className="hidden sm:inline">Refresh data</span>
            </Button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-[1580px] px-5 py-7 lg:px-8 lg:py-10">
        <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_470px] xl:items-end">
          <div>
            <p className="mb-3 text-xs font-bold uppercase tracking-[0.17em] text-[#61756b]">Today’s shortlist · {formatDate(data.run.date)}</p>
            <h1 className="max-w-4xl text-4xl font-semibold tracking-[-0.055em] sm:text-5xl lg:text-6xl">Strong roles, clearly ranked.</h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-[#68756e]">Review high-fit remote engineering opportunities, understand the rationale, and move every application forward from one focused workspace.</p>
          </div>
          <div className="grid grid-cols-3 overflow-hidden rounded-2xl border border-[#d7ded8] bg-white shadow-[0_18px_45px_rgba(31,61,45,0.055)]">
            {[
              [data.summary.distinct_candidates_reviewed, 'Found'],
              [data.summary.passed_all_filters, 'Matched'],
              [data.summary.rejected_or_unverifiable, 'Filtered'],
            ].map(([value, label], index) => (
              <div key={label} className={`p-5 sm:p-6 ${index ? 'border-l border-[#e1e6e1]' : ''}`}>
                <p className="text-3xl font-semibold tracking-[-0.045em] tabular-nums">{value}</p>
                <p className="mt-1 text-xs font-medium text-[#7a867e]">{label}</p>
              </div>
            ))}
          </div>
        </section>

        {notice && (
          <div role="status" className="mt-6 flex items-start gap-3 rounded-xl border border-[#e4dcc2] bg-[#fff9e9] px-4 py-3 text-sm text-[#705f35]">
            {backendAvailable ? <Check className="mt-0.5 shrink-0" size={16} /> : <CloudOff className="mt-0.5 shrink-0" size={16} />}
            {notice}
          </div>
        )}

        <section className="mt-8 grid gap-4 lg:grid-cols-3">
          {data.top_three.slice(0, 3).map((pick, index) => (
            <article key={`${pick.company}-${pick.rank}`} className="relative overflow-hidden rounded-2xl border border-[#d9e0da] bg-[#183f31] p-5 text-white shadow-[0_16px_40px_rgba(24,63,49,0.11)] sm:p-6">
              <span className="absolute right-4 top-2 text-7xl font-bold tracking-[-0.08em] text-white/[0.055]">0{index + 1}</span>
              <p className="relative flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.14em] text-[#add0bf]"><Sparkles size={13} /> Top pick</p>
              <h2 className="relative mt-3 text-xl font-semibold tracking-[-0.025em]">{pick.company}</h2>
              <p className="relative mt-2 text-sm leading-6 text-[#d6e2dc]">{pick.reason}</p>
            </article>
          ))}
        </section>

        <div className="mt-8"><RunInsights data={data} /></div>

        <div className="mt-8"><Filters filters={filters} jobs={data.jobs} onChange={setFilter} onClear={clearFilters} /></div>

        <section className="mt-5">
          <div className="mb-4 flex items-center justify-between gap-4">
            <p className="text-sm font-semibold text-[#33473d]">{visibleJobs.length} {visibleJobs.length === 1 ? 'role' : 'roles'} shown</p>
            <p className="hidden text-xs text-[#7b877f] sm:block">Source: {data.run.source_file}</p>
          </div>
          {visibleJobs.length ? (
            <div className="grid gap-4 lg:grid-cols-2 2xl:grid-cols-3">
              {visibleJobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  busy={mutatingJobId === job.id}
                  canPersist={backendAvailable}
                  onStatus={(status) => void updateStatus(job.id, status)}
                  onCoverLetter={() => void generateCoverLetter(job.id, job.suggested_resume)}
                />
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-[#cbd5cd] bg-white px-6 py-16 text-center">
              <p className="font-semibold">No roles match this filter combination.</p>
              <p className="mt-2 text-sm text-[#728078]">Clear one or more filters to widen the shortlist.</p>
              <Button className="mt-5" variant="secondary" onClick={clearFilters}>Clear filters</Button>
            </div>
          )}
        </section>
      </div>

      <Dialog open={coverLetterOpen} onOpenChange={setCoverLetterOpen}>
        <DialogContent>
          <div className="pr-10">
            <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-[#61756b]">{coverLetter?.mode === 'openai' ? 'AI-generated draft' : coverLetter?.mode === 'local' ? 'Local draft' : 'Preview draft'}</p>
            <DialogTitle className="mt-2 text-2xl font-semibold tracking-[-0.035em]">Your tailored cover letter</DialogTitle>
            <DialogDescription className="mt-2 text-sm leading-6 text-[#6a776f]">Review every statement before using it. The generator is instructed not to invent candidate experience.</DialogDescription>
          </div>
          {coverLetter?.warning && <p className="mt-4 rounded-xl bg-[#fff6df] p-3 text-sm text-[#735c24]">{coverLetter.warning}</p>}
          <pre className="mt-6 whitespace-pre-wrap rounded-2xl border border-[#dce2dd] bg-white p-5 font-sans text-sm leading-7 text-[#33443b]">{coverLetter?.content}</pre>
          <div className="mt-5 flex flex-wrap justify-end gap-2">
            <Button variant="secondary" onClick={() => void copyLetter()}><Clipboard size={15} /> Copy</Button>
            <Button onClick={downloadLetter}><Download size={15} /> Download .txt</Button>
          </div>
        </DialogContent>
      </Dialog>
    </main>
  );
}

