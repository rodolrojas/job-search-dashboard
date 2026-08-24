'use client';

import { AtSign, Building2, CalendarDays, Check, FilePenLine, FileText, Link2, LoaderCircle, MapPin, Sparkles, X } from 'lucide-react';
import type { Job } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { cn, formatDate, shortResumeName } from '@/lib/utils';

interface JobCardProps {
  job: Job;
  busy: boolean;
  canPersist: boolean;
  onStatus: (status: 'applied' | 'rejected') => void;
  onCoverLetter: () => void;
}

function scoreStyle(score: number) {
  if (score >= 70) return 'bg-[#dcefe5] text-[#176343] dark:bg-[#193d2d] dark:text-[#8bd4af]';
  if (score >= 50) return 'bg-[#fff0c6] text-[#8a5b06] dark:bg-[#463812] dark:text-[#f1c96b]';
  return 'bg-[#fbe1de] text-[#a43730] dark:bg-[#49231f] dark:text-[#efa49e]';
}

export function JobCard({ job, busy, canPersist, onStatus, onCoverLetter }: JobCardProps) {
  const applied = job.status === 'applied';
  const rejected = job.status === 'rejected';

  return (
    <article className={cn(
      'group relative flex min-h-[520px] flex-col overflow-hidden rounded-2xl border bg-white p-5 shadow-[0_14px_38px_rgba(31,61,45,0.045)] transition hover:-translate-y-0.5 hover:shadow-[0_18px_45px_rgba(31,61,45,0.08)] dark:bg-[#15211b] dark:shadow-black/20 dark:hover:shadow-black/30 sm:p-6',
      applied ? 'border-[#9fceb7] dark:border-[#39785a]' : rejected ? 'border-[#e8b5b0] opacity-75 dark:border-[#75423d]' : 'border-[#d9e0da] dark:border-[#2c3c34]',
    )}>
      {job.is_new && (
        <span className="absolute left-0 top-0 rounded-br-xl bg-[#dceafa] px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.14em] text-[#2d5d91]">
          New
        </span>
      )}
      <div className={cn('flex items-start justify-between gap-5', job.is_new && 'pt-4')}>
        <div className="min-w-0">
          <p className="flex items-center gap-2 text-xs font-semibold text-[#637168] dark:text-[#9fb0a7]">
            <Building2 size={13} /> {job.company}
          </p>
          <h2 className="mt-2 text-xl font-semibold leading-[1.2] tracking-[-0.035em] text-[#18251f] dark:text-[#edf4f0] sm:text-[22px]">
            {job.role}
          </h2>
        </div>
        <span aria-label={`Match score ${job.score}`} className={cn('grid size-12 shrink-0 place-items-center rounded-xl text-lg font-bold tabular-nums', scoreStyle(job.score))}>
          {job.score}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-xs text-[#6a776f] dark:text-[#a7b6ae]">
        <span className="flex items-center gap-1.5"><MapPin size={13} /> {job.location}</span>
        <span className="flex items-center gap-1.5"><CalendarDays size={13} /> {formatDate(job.posted)}</span>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <span className="rounded-full bg-[#f0f4f0] px-3 py-1.5 text-xs font-medium text-[#516158] dark:bg-[#223129] dark:text-[#b4c4bb]">{job.employment_type}</span>
        <span className="rounded-full bg-[#f0f4f0] px-3 py-1.5 text-xs font-medium text-[#516158] dark:bg-[#223129] dark:text-[#b4c4bb]">{job.salary}</span>
      </div>

      {job.score >= 70 && job.strategic_note && (
        <div className="mt-5 rounded-xl border border-[#dfe7df] bg-[#f7f9f6] p-4 dark:border-[#304139] dark:bg-[#111c16]">
          <p className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.14em] text-[#5c7468] dark:text-[#9bb4a7]">
            <Sparkles size={13} /> Strategic note
          </p>
          <p className="mt-2 line-clamp-4 text-sm leading-6 text-[#526158] dark:text-[#b0c0b7]">{job.strategic_note}</p>
        </div>
      )}

      <section aria-label="Suggested resume" className="mt-4 rounded-xl border border-[#cfe0d7] bg-[#edf6f1] p-4 dark:border-[#315944] dark:bg-[#152b20]">
        <p className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.14em] text-[#3e6d57] dark:text-[#8fc8ab]">
          <FileText size={13} /> Suggested resume
        </p>
        <p className="mt-2 text-sm font-semibold text-[#244b38] dark:text-[#d0e8dc]">{shortResumeName(job.suggested_resume)}</p>
        <p className="mt-1 break-all text-xs text-[#6b7c73] dark:text-[#9fb2a8]">{job.suggested_resume}</p>
      </section>

      <div className="mt-5 space-y-2 text-sm">
        {job.contact_email && (
          <a href={`mailto:${job.contact_email}`} className="flex items-center gap-2 text-[#315f4b] underline-offset-4 hover:underline dark:text-[#91c9ac]">
            <AtSign size={15} /> {job.contact_email}
          </a>
        )}
        {job.offer_url && (
          <a href={job.offer_url} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-[#315f4b] underline-offset-4 hover:underline dark:text-[#91c9ac]">
            <Link2 size={15} /> Open job listing
          </a>
        )}
        {job.recruiter_or_careers_url && (
          <a href={job.recruiter_or_careers_url} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-[#315f4b] underline-offset-4 hover:underline dark:text-[#91c9ac]">
            <Link2 size={15} /> Recruiter or careers page
          </a>
        )}
      </div>

      <div className="mt-auto grid gap-2 pt-6 sm:grid-cols-2">
        <Button variant="success" size="sm" onClick={() => onStatus('applied')} disabled={busy || applied || rejected || !canPersist} title={!canPersist ? 'Start the Flask service to save this status' : undefined}>
          {busy ? <LoaderCircle className="animate-spin" size={14} /> : <Check size={14} />}
          {applied ? 'Applied' : 'Mark as Applied'}
        </Button>
        <Button variant="destructive" size="sm" onClick={() => onStatus('rejected')} disabled={busy || applied || rejected || !canPersist} title={!canPersist ? 'Start the Flask service to save this status' : undefined}>
          <X size={14} /> {rejected ? 'Rejected' : 'Mark as Rejected'}
        </Button>
        <Button variant="secondary" size="sm" className="sm:col-span-2" onClick={onCoverLetter} disabled={busy}>
          <FilePenLine size={14} /> Generate Cover Letter
        </Button>
      </div>
    </article>
  );
}
