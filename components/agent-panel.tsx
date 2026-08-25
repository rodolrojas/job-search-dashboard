import { Bot, CheckCircle2, CircleDot, LoaderCircle, Play, SearchCheck, ShieldCheck, SquareTerminal } from 'lucide-react';
import type { AgentInfo, AgentRun } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface AgentPanelProps {
  info?: AgentInfo;
  run?: AgentRun;
  backendAvailable: boolean;
  starting: boolean;
  onStart: () => void;
}

const phaseLabels: Record<string, string> = {
  plan: 'Plan queries',
  research: 'Search the web',
  validate: 'Validate listings',
  score: 'Score profile fit',
  persist: 'Save the run',
  complete: 'Complete',
};

export function AgentPanel({ info, run, backendAvailable, starting, onStart }: AgentPanelProps) {
  const active = run?.status === 'queued' || run?.status === 'running';
  const ready = backendAvailable && Boolean(info?.configured);
  const recentEvents = run?.events.slice(-5) ?? [];

  return (
    <section className="mt-8 overflow-hidden rounded-2xl border border-[#bfd5c8] bg-[#eaf4ee] shadow-[0_18px_45px_rgba(24,63,49,0.06)] dark:border-[#315441] dark:bg-[#12271d]">
      <div className="grid gap-6 p-5 sm:p-6 xl:grid-cols-[minmax(0,1fr)_430px] xl:p-7">
        <div>
          <p className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.16em] text-[#47705c] dark:text-[#8fc5a8]">
            <Bot size={14} /> Inspectable AI agent
          </p>
          <h2 className="mt-3 text-2xl font-semibold tracking-[-0.04em] sm:text-3xl">Research a fresh shortlist</h2>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-[#5a6f63] dark:text-[#acc0b5]">
            The Python agent plans targeted searches, asks the signed-in Codex instance on this machine to research and score, validates every direct listing URL and date, then writes a new JSON run for this dashboard.
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            {(info?.workflow ?? ['plan', 'research', 'validate', 'score', 'persist']).map((phase, index) => (
              <span key={phase} className="flex items-center gap-2 rounded-full border border-[#c8dbd0] bg-white/70 px-3 py-1.5 text-xs font-semibold text-[#41604f] dark:border-[#315441] dark:bg-[#183326] dark:text-[#b8d3c4]">
                <span className="text-[#7b9587]">{index + 1}</span> {phaseLabels[phase] ?? phase}
              </span>
            ))}
          </div>

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Button onClick={onStart} disabled={!ready || active || starting}>
              {active || starting ? <LoaderCircle className="animate-spin" size={15} /> : <Play size={15} />}
              {active ? 'Agent running' : starting ? 'Starting…' : 'Run AI search'}
            </Button>
            <span className={cn(
              'flex items-center gap-2 text-xs font-medium',
              ready ? 'text-[#3f6753] dark:text-[#9fc9b2]' : 'text-[#806832] dark:text-[#d3b96e]',
            )}>
              {ready ? <SearchCheck size={15} /> : <SquareTerminal size={15} />}
              {!backendAvailable ? 'Start the Flask API to run it' : info?.configured ? `${info.provider} · ${info.model} · ${info.prompt_file}` : info?.runtime ?? 'Install and sign in to Codex CLI on this machine'}
            </span>
          </div>

          <p className="mt-5 flex items-start gap-2 text-xs leading-5 text-[#61766a] dark:text-[#9eb3a7]">
            <ShieldCheck className="mt-0.5 shrink-0" size={14} />
            Research only: it never submits applications, bypasses login walls, or trusts an unvalidated listing.
          </p>
        </div>

        <aside className="rounded-2xl border border-[#cfdfd5] bg-white/75 p-4 dark:border-[#315441] dark:bg-[#0e1d16]/70">
          <div className="flex items-center justify-between gap-3">
            <p className="text-xs font-bold uppercase tracking-[0.12em] text-[#587064] dark:text-[#91ad9d]">Agent activity</p>
            {run && (
              <span className={cn(
                'rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.1em]',
                run.status === 'completed' ? 'bg-[#dcefe5] text-[#176343] dark:bg-[#193d2d] dark:text-[#8bd4af]' :
                  run.status === 'failed' ? 'bg-[#fbe4e1] text-[#9e3029] dark:bg-[#49231f] dark:text-[#efa49e]' :
                    'bg-[#e6eef8] text-[#335f8d] dark:bg-[#1c344b] dark:text-[#9cc2e5]',
              )}>{run.status}</span>
            )}
          </div>

          {run ? (
            <div className="mt-4 space-y-3">
              {recentEvents.length ? recentEvents.map((event, index) => (
                <div key={`${event.created_at}-${index}`} className="flex gap-3 text-sm">
                  {index === recentEvents.length - 1 && active
                    ? <LoaderCircle className="mt-0.5 shrink-0 animate-spin text-[#3f765a]" size={15} />
                    : <CheckCircle2 className="mt-0.5 shrink-0 text-[#5d9075]" size={15} />}
                  <div>
                    <p className="font-semibold text-[#31483c] dark:text-[#c7d9cf]">{phaseLabels[event.phase] ?? event.phase}</p>
                    <p className="mt-0.5 text-xs leading-5 text-[#6d7c74] dark:text-[#9eafa6]">{event.message}</p>
                  </div>
                </div>
              )) : (
                <p className="flex items-center gap-2 text-sm text-[#6d7c74] dark:text-[#9eafa6]"><CircleDot size={14} /> {run.message}</p>
              )}
              {run.error && <p className="rounded-xl bg-[#fff1ef] p-3 text-xs leading-5 text-[#8d3831] dark:bg-[#3e211e] dark:text-[#efaaa3]">{run.error}</p>}
            </div>
          ) : (
            <p className="mt-4 text-sm leading-6 text-[#6d7c74] dark:text-[#9eafa6]">No run has started in this API process. Start one to watch each decision stage appear here.</p>
          )}
        </aside>
      </div>
    </section>
  );
}
