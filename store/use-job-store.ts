'use client';

import { useSyncExternalStore } from 'react';
import { createStore } from 'zustand/vanilla';
import { api } from '@/lib/api';
import type { CoverLetterResult, DashboardData, JobFilters, JobStatus } from '@/lib/types';
import { demoDashboard } from '@/data/demo-dashboard';

interface JobStore {
  data: DashboardData;
  filters: JobFilters;
  loading: boolean;
  mutatingJobId?: string;
  backendAvailable: boolean;
  notice?: string;
  coverLetter?: CoverLetterResult;
  coverLetterOpen: boolean;
  load: () => Promise<void>;
  setFilter: <K extends keyof JobFilters>(key: K, value: JobFilters[K]) => void;
  clearFilters: () => void;
  updateStatus: (jobId: string, status: Exclude<JobStatus, 'available'>) => Promise<void>;
  generateCoverLetter: (jobId: string, resumeVariant: string) => Promise<void>;
  setCoverLetterOpen: (open: boolean) => void;
}

const defaultFilters: JobFilters = {
  query: '',
  minScore: 0,
  company: '',
  location: '',
  status: 'all',
  sort: 'score_desc',
};

const jobStore = createStore<JobStore>((set, get) => ({
  data: demoDashboard,
  filters: defaultFilters,
  loading: true,
  backendAvailable: false,
  coverLetterOpen: false,
  async load() {
    set({ loading: true, notice: undefined });
    try {
      const response = await api.get<DashboardData>('/dashboard');
      set({ data: response.data, backendAvailable: true, loading: false });
    } catch {
      set({
        data: demoDashboard,
        backendAvailable: false,
        loading: false,
        notice: 'Preview mode is active. Start the Flask service to save job statuses and generated files.',
      });
    }
  },
  setFilter(key, value) {
    set((state) => ({ filters: { ...state.filters, [key]: value } }));
  },
  clearFilters() {
    set({ filters: defaultFilters });
  },
  async updateStatus(jobId, status) {
    if (!get().backendAvailable) {
      set({ notice: 'Saving status requires the local Flask service.' });
      return;
    }
    set({ mutatingJobId: jobId, notice: undefined });
    try {
      await api.post(`/jobs/${encodeURIComponent(jobId)}/status`, { status });
      set((state) => ({
        data: {
          ...state.data,
          jobs: state.data.jobs.map((job) => (job.id === jobId ? { ...job, status } : job)),
        },
        notice: status === 'applied' ? 'Application status saved.' : 'Role rejected and excluded from future results.',
      }));
    } catch {
      set({ notice: 'The status could not be saved. Check that the Flask service is running.' });
    } finally {
      set({ mutatingJobId: undefined });
    }
  },
  async generateCoverLetter(jobId, resumeVariant) {
    const job = get().data.jobs.find((item) => item.id === jobId);
    if (!job) return;
    set({ mutatingJobId: jobId, notice: undefined });
    try {
      if (get().backendAvailable) {
        const response = await api.post<CoverLetterResult>(`/jobs/${encodeURIComponent(jobId)}/cover-letter`, {
          resume_variant: resumeVariant,
        });
        set({ coverLetter: response.data, coverLetterOpen: true });
      } else {
        const content = `Dear ${job.company} Hiring Team,\n\nI am writing to apply for the ${job.role} position. With more than ten years of experience delivering production web applications and backend services, I bring strong product ownership across frontend, backend, data, cloud delivery, and production support.\n\n${job.strategic_note || 'The role aligns closely with my software engineering background.'} I would use the ${resumeVariant.replaceAll('_', ' ')} resume variant to foreground the experience most relevant to this opportunity.\n\nI would welcome the opportunity to discuss how my background can help ${job.company} deliver reliable product outcomes.\n\nSincerely,\nRodolfo Rojas\n`;
        set({
          coverLetter: { content, mode: 'preview', filename: `${job.company.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-cover-letter.txt` },
          coverLetterOpen: true,
          notice: 'Preview draft created. Start the Flask service to save it or use the OpenAI integration.',
        });
      }
    } catch {
      set({ notice: 'The cover letter could not be generated. Check the backend configuration and try again.' });
    } finally {
      set({ mutatingJobId: undefined });
    }
  },
  setCoverLetterOpen(open) {
    set({ coverLetterOpen: open });
  },
}));

export function useJobStore(): JobStore {
  return useSyncExternalStore(jobStore.subscribe, jobStore.getState, jobStore.getInitialState);
}
