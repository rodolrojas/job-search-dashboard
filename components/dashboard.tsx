'use client';

import { useEffect, useMemo } from 'react';
import { BriefcaseBusiness, Check, Clipboard, CloudOff, Download, Moon, RefreshCw, Sparkles, Sun } from 'lucide-react';
import { Filters } from '@/components/filters';
import { AgentPanel } from '@/components/agent-panel';
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
    agentInfo,
    agentRun,
    agentStarting,
    load,
    setFilter,
    clearFilters,
    updateStatus,
    generateCoverLetter,
    startAgent,
    setCoverLetterOpen,
  } = useJobStore();

  useEffect(() => { void load(); }, [load]);

  const toggleTheme = () => {
    const nextDarkMode = !document.documentElement.classList.contains('dark');
    document.documentElement.classList.toggle('dark', nextDarkMode);
    localStorage.setItem('role-radar-theme', nextDarkMode ? 'dark' : 'light');
  };

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
    <main className="min-h-screen bg-[#f5f7f4] text-[#18231e] transition-colors dark:bg-[#0d1511] dark:text-[#e8f0eb]">
      <header className="sticky top-0 z-40 border-b border-[#dce2dd] bg-[#f5f7f4]/92 backdrop-blur-xl transition-colors dark:border-[#26352d] dark:bg-[#0d1511]/92">
        <div className="mx-auto flex max-w-[1580px] items-center justify-between gap-4 px-5 py-4 lg:px-8">
          <div className="flex items-center gap-3">
            <span className="grid size-10 place-items-center rounded-xl bg-[#183f31] text-white shadow-[0_8px_20px_rgba(24,63,49,0.18)]"><BriefcaseBusiness size={19} /></span>
            <div>
              <p className="font-semibold tracking-[-0.025em]">Role Radar</p>
              <p className="text-[11px] text-[#6e7b73] dark:text-[#9caea4]">Job search command center</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="hidden items-center gap-2 rounded-full border border-[#d7ded8] bg-white px-3 py-2 text-xs text-[#56645c] dark:border-[#304139] dark:bg-[#15211b] dark:text-[#b9c9c0] md:flex">
              <span className={`size-2 rounded-full ${backendAvailable ? 'bg-[#42a675]' : 'bg-[#e0a43a]'}`} />
              {backendAvailable ? 'Live workspace' : 'Preview mode'}
            </span>
            <Button
              variant="secondary"
              size="icon"
              onClick={toggleTheme}
              aria-label="Toggle color theme"
              title="Toggle color theme"
            >
              <Moon className="dark:hidden" size={16} />
              <Sun className="hidden dark:block" size={16} />
            </Button>
            <Button variant="secondary" size="sm" onClick={() => void load()} disabled={loading}>
              <RefreshCw className={loading ? 'animate-spin' : ''} size={14} /> <span className="hidden sm:inline">Refresh data</span>
            </Button>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-[1580px] px-5 py-7 lg:px-8 lg:py-10">
        <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_470px] xl:items-end">
          <div>
            <p className="mb-3 text-xs font-bold uppercase tracking-[0.17em] text-[#61756b] dark:text-[#9fb6a9]">Today’s shortlist · {formatDate(data.run.date)}</p>
            <h1 className="max-w-4xl text-4xl font-semibold tracking-[-0.055em] sm:text-5xl lg:text-6xl">Strong roles, clearly ranked.</h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-[#68756e] dark:text-[#a8b8af]">Review high-fit remote engineering opportunities, understand the rationale, and move every application forward from one focused workspace.</p>
          </div>
          <div className="grid grid-cols-3 overflow-hidden rounded-2xl border border-[#d7ded8] bg-white shadow-[0_18px_45px_rgba(31,61,45,0.055)] dark:border-[#2c3c34] dark:bg-[#15211b] dark:shadow-black/20">
            {[
              [data.summary.distinct_candidates_reviewed, 'Found'],
              [data.summary.passed_all_filters, 'Matched'],
              [data.summary.rejected_or_unverifiable, 'Filtered'],
            ].map(([value, label], index) => (
              <div key={label} className={`p-5 sm:p-6 ${index ? 'border-l border-[#e1e6e1] dark:border-[#2c3c34]' : ''}`}>
                <p className="text-3xl font-semibold tracking-[-0.045em] tabular-nums">{value}</p>
                <p className="mt-1 text-xs font-medium text-[#7a867e] dark:text-[#9cadA4]">{label}</p>
              </div>
            ))}
          </div>
        </section>

        {notice && (
          <div role="status" className="mt-6 flex items-start gap-3 rounded-xl border border-[#e4dcc2] bg-[#fff9e9] px-4 py-3 text-sm text-[#705f35] dark:border-[#5a4b2a] dark:bg-[#2a2415] dark:text-[#e5ca86]">
            {backendAvailable ? <Check className="mt-0.5 shrink-0" size={16} /> : <CloudOff className="mt-0.5 shrink-0" size={16} />}
            {notice}
          </div>
        )}

        <AgentPanel
          info={agentInfo}
          run={agentRun}
          backendAvailable={backendAvailable}
          starting={agentStarting}
          onStart={() => void startAgent()}
        />

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
            <p className="text-sm font-semibold text-[#33473d] dark:text-[#c5d4cc]">{visibleJobs.length} {visibleJobs.length === 1 ? 'role' : 'roles'} shown</p>
            <p className="hidden text-xs text-[#7b877f] dark:text-[#91a299] sm:block">Source: {data.run.source_file}</p>
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
            <div className="rounded-2xl border border-dashed border-[#cbd5cd] bg-white px-6 py-16 text-center dark:border-[#3a4b42] dark:bg-[#15211b]">
              <p className="font-semibold">No roles match this filter combination.</p>
              <p className="mt-2 text-sm text-[#728078] dark:text-[#a0b0a7]">Clear one or more filters to widen the shortlist.</p>
              <Button className="mt-5" variant="secondary" onClick={clearFilters}>Clear filters</Button>
            </div>
          )}
        </section>
      </div>

      <Dialog open={coverLetterOpen} onOpenChange={setCoverLetterOpen}>
        <DialogContent>
          <div className="pr-10">
            <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-[#61756b] dark:text-[#9eb3a8]">{coverLetter?.mode === 'codex' ? 'Codex-generated draft' : coverLetter?.mode === 'local' ? 'Local draft' : 'Preview draft'}</p>
            <DialogTitle className="mt-2 text-2xl font-semibold tracking-[-0.035em]">Your tailored cover letter</DialogTitle>
            <DialogDescription className="mt-2 text-sm leading-6 text-[#6a776f] dark:text-[#a7b7ae]">Review every statement before using it. The generator is instructed not to invent candidate experience.</DialogDescription>
          </div>
          {coverLetter?.warning && <p className="mt-4 rounded-xl bg-[#fff6df] p-3 text-sm text-[#735c24] dark:bg-[#302713] dark:text-[#e5ca86]">{coverLetter.warning}</p>}
          <pre className="mt-6 whitespace-pre-wrap rounded-2xl border border-[#dce2dd] bg-white p-5 font-sans text-sm leading-7 text-[#33443b] dark:border-[#304139] dark:bg-[#111c16] dark:text-[#cedbd4]">{coverLetter?.content}</pre>
          <div className="mt-5 flex flex-wrap justify-end gap-2">
            <Button variant="secondary" onClick={() => void copyLetter()}><Clipboard size={15} /> Copy</Button>
            <Button onClick={downloadLetter}><Download size={15} /> Download .txt</Button>
          </div>
        </DialogContent>
      </Dialog>
    </main>
  );
}
