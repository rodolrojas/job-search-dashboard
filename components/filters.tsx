'use client';

import { RotateCcw, Search, SlidersHorizontal } from 'lucide-react';
import type { Job, JobFilters } from '@/lib/types';
import { Button } from '@/components/ui/button';

interface FiltersProps {
  filters: JobFilters;
  jobs: Job[];
  onChange: <K extends keyof JobFilters>(key: K, value: JobFilters[K]) => void;
  onClear: () => void;
}

const selectClass = 'h-11 min-w-0 rounded-xl border border-[#d7ded8] bg-white px-3 text-sm text-[#33473d] outline-none focus:border-[#6e9381] focus:ring-2 focus:ring-[#cfe1d8] dark:border-[#304139] dark:bg-[#111c16] dark:text-[#c6d5cd] dark:focus:border-[#6ca88b] dark:focus:ring-[#294a3a]';

export function Filters({ filters, jobs, onChange, onClear }: FiltersProps) {
  const companies = [...new Set(jobs.map((job) => job.company))].sort();
  const locations = [...new Set(jobs.map((job) => job.location))].sort();
  const dirty = filters.query || filters.minScore || filters.company || filters.location || filters.status !== 'all' || filters.sort !== 'score_desc';

  return (
    <section aria-label="Job filters" className="rounded-2xl border border-[#d9e0da] bg-white p-3 shadow-[0_12px_34px_rgba(31,61,45,0.045)] dark:border-[#2c3c34] dark:bg-[#15211b] dark:shadow-black/20">
      <div className="grid gap-3 xl:grid-cols-[minmax(220px,1.7fr)_repeat(5,minmax(132px,1fr))_auto]">
        <label className="flex h-11 items-center gap-3 rounded-xl bg-[#f2f5f2] px-4 text-[#6a776f] focus-within:ring-2 focus-within:ring-[#cfe1d8] dark:bg-[#111c16] dark:text-[#a3b4aa] dark:focus-within:ring-[#294a3a]">
          <Search size={17} aria-hidden="true" />
          <span className="sr-only">Search roles</span>
          <input
            value={filters.query}
            onChange={(event) => onChange('query', event.target.value)}
            className="w-full bg-transparent text-sm text-[#273a31] outline-none placeholder:text-[#8a958e] dark:text-[#d2ddd7] dark:placeholder:text-[#73857b]"
            placeholder="Search role, company, skill…"
          />
        </label>

        <label className="sr-only" htmlFor="score-filter">Minimum score</label>
        <select id="score-filter" className={selectClass} value={filters.minScore} onChange={(event) => onChange('minScore', Number(event.target.value))}>
          <option value={0}>Any score</option>
          <option value={70}>70+ fit</option>
          <option value={85}>85+ strong</option>
          <option value={90}>90+ top fit</option>
        </select>

        <label className="sr-only" htmlFor="company-filter">Company</label>
        <select id="company-filter" className={selectClass} value={filters.company} onChange={(event) => onChange('company', event.target.value)}>
          <option value="">All companies</option>
          {companies.map((company) => <option key={company} value={company}>{company}</option>)}
        </select>

        <label className="sr-only" htmlFor="location-filter">Location</label>
        <select id="location-filter" className={selectClass} value={filters.location} onChange={(event) => onChange('location', event.target.value)}>
          <option value="">All locations</option>
          {locations.map((location) => <option key={location} value={location}>{location}</option>)}
        </select>

        <label className="sr-only" htmlFor="status-filter">Status</label>
        <select id="status-filter" className={selectClass} value={filters.status} onChange={(event) => onChange('status', event.target.value as JobFilters['status'])}>
          <option value="all">All statuses</option>
          <option value="available">Available</option>
          <option value="applied">Applied</option>
          <option value="rejected">Rejected</option>
        </select>

        <label className="sr-only" htmlFor="sort-filter">Sort roles</label>
        <select id="sort-filter" className={selectClass} value={filters.sort} onChange={(event) => onChange('sort', event.target.value as JobFilters['sort'])}>
          <option value="score_desc">Best score</option>
          <option value="date_desc">Newest first</option>
          <option value="company_asc">Company A–Z</option>
          <option value="role_asc">Role A–Z</option>
        </select>

        <Button variant="ghost" size="icon" onClick={onClear} disabled={!dirty} title="Clear all filters" aria-label="Clear all filters">
          <RotateCcw size={17} />
        </Button>
      </div>
      <div className="mt-3 flex items-center gap-2 px-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-[#849087] dark:text-[#899b91] xl:hidden">
        <SlidersHorizontal size={13} /> Multiple filters can be combined
      </div>
    </section>
  );
}
