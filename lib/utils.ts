import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(value?: string) {
  if (!value) return 'Date unavailable';
  const parsed = new Date(`${value.slice(0, 10)}T12:00:00`);
  if (Number.isNaN(parsed.valueOf())) return value;
  return new Intl.DateTimeFormat('en', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(parsed);
}

export function shortResumeName(value: string) {
  return value
    .replace('Rodolfo_Rojas_', '')
    .replace('_CV.pdf', '')
    .replaceAll('_', ' / ');
}

export function comparisonLabel(item: string | { role?: string; reason?: string }) {
  return typeof item === 'string' ? item : item.role || item.reason || 'Updated role';
}

