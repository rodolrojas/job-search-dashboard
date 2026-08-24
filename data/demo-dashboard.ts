import type { DashboardData, Job } from '@/lib/types';

const common = {
  employment_type: 'Full-time',
  status: 'available' as const,
  is_new: false,
};

const jobs: Job[] = [
  {
    ...common,
    id: 'tecla-3361-4456795759', rank: 1, is_new: true, role: 'Sr. Full-Stack Developer', company: 'Tecla', location: 'Latin America — Remote', posted: '2026-08-20', score: 95, salary: 'USD 4,000/month', offer_url: 'https://app.tecla.io/job?id=3361', recruiter_or_careers_url: 'https://www.linkedin.com/company/tecla-io/life/', suggested_resume: 'Rodolfo_Rojas_React_Node_CV.pdf', strategic_note: 'The strongest new match: Next.js, TypeScript, PostgreSQL, AWS, product ownership, architecture, and startup execution, with disclosed pay and region-wide scope.',
  },
  {
    ...common,
    id: 'reap-8140235-4446547642', rank: 2, role: 'Senior Software Engineer, Treasury (LATAM)', company: 'Reap', location: 'LATAM — Remote', posted: '2026-08-19', score: 94, salary: 'Undisclosed', offer_url: 'https://careers.reap.global/jobs/8140235-senior-software-engineer-treasury-latam', recruiter_or_careers_url: 'https://careers.reap.global/', suggested_resume: 'Rodolfo_Rojas_Backend_CV.pdf', strategic_note: 'Excellent backend alignment across TypeScript, Node.js, NestJS, AWS, PostgreSQL, asynchronous workflows, reliability, and incident ownership.',
  },
  {
    ...common,
    id: 'deel-4448218797', rank: 3, role: 'Senior Fullstack Engineer, NodeJS & ReactJS | LATAM', company: 'Deel', location: 'LATAM — Remote', posted: '2026-08-06', score: 91, salary: 'Undisclosed', offer_url: 'https://www.linkedin.com/jobs/view/senior-fullstack-engineer-nodejs-reactjs-latam-at-deel-4448218797/', contact_email: 'recruiting@deel.com', recruiter_or_careers_url: 'https://www.deel.com/careers/', suggested_resume: 'Rodolfo_Rojas_React_Node_CV.pdf', strategic_note: 'A close Node.js, TypeScript, React, PostgreSQL, SaaS, microservices, Docker, and AWS-adjacent fit.',
  },
  {
    ...common,
    id: 'avenue-code-4380615408', rank: 4, role: 'Senior Fullstack Developer (Next.js / Node.js / Microservices)', company: 'Avenue Code', location: 'Latin America — Remote', posted: '2026-08-06', score: 91, salary: 'Undisclosed', offer_url: 'https://www.linkedin.com/jobs/view/4380615408/', recruiter_or_careers_url: 'https://www.avenuecode.com/careers', suggested_resume: 'Rodolfo_Rojas_React_Node_CV.pdf', strategic_note: 'Strong TypeScript, Node, Next.js, PostgreSQL, microservices, event-driven messaging, CI/CD, code review, and mentoring alignment.',
  },
  {
    ...common,
    id: 'tecla-3274-4447087044', rank: 5, role: 'Sr. Software Engineer', company: 'Tecla', location: 'Latin America — Remote / US Pacific overlap', posted: '2026-08-19', score: 90, salary: 'USD 3,500–4,500/month', offer_url: 'https://app.tecla.io/job?id=3274', recruiter_or_careers_url: 'https://www.linkedin.com/company/tecla-io/life/', suggested_resume: 'Rodolfo_Rojas_Frontend_CV.pdf', strategic_note: 'A compelling React and TypeScript product role with architecture, project leadership, mentoring, code review, and disclosed pay.',
  },
  {
    ...common,
    id: 'audienceview-4435807228', rank: 6, role: 'Senior Software Developer', company: 'AudienceView', location: 'Chile — Remote-first', posted: '2026-08-13', score: 89, salary: 'Undisclosed', offer_url: 'https://www.linkedin.com/jobs/view/4435807228/', recruiter_or_careers_url: 'https://audienceview.com/careers/', suggested_resume: 'Rodolfo_Rojas_React_Node_CV.pdf', strategic_note: 'Strong React, TypeScript, Node.js, SQL, Redis, SaaS modernization, architecture review, ownership, and mentoring alignment.',
  },
  {
    ...common,
    id: 'cit-4455948521', rank: 7, role: 'Senior Node.js / React / AI Full-Stack Developer', company: 'CI&T', location: 'Brazil — Remote', posted: '2026-08-19', score: 89, salary: 'Undisclosed', offer_url: 'https://www.linkedin.com/jobs/view/4455948521/', contact_email: 'attractingtalk@ciandt.com', recruiter_or_careers_url: 'https://ciandt.com/br/pt-br/carreiras', suggested_resume: 'Rodolfo_Rojas_React_Node_CV.pdf', strategic_note: 'Direct Node.js and React fit with APIs, microservices, autonomous technical refinement, code reviews, continuous delivery, and AI-assisted development.',
  },
  {
    ...common,
    id: 'sezzle-4335397387', rank: 8, role: 'Senior Software Engineer (Chile)', company: 'Sezzle', location: 'Santiago, Chile — Remote', posted: '2026-08-13', score: 87, salary: 'USD 5,000–9,500/month', offer_url: 'https://www.linkedin.com/jobs/view/4335397387/', recruiter_or_careers_url: 'https://sezzle.com/careers/', suggested_resume: 'Rodolfo_Rojas_Go_CV.pdf', strategic_note: 'A credible Go-transition opportunity with React, PostgreSQL, AWS, queues, APIs, distributed systems, mentoring, and verified compensation.',
  },
  {
    ...common,
    id: 'air-4452888171', rank: 9, role: 'Node.js Full-Stack Developer | Senior', company: 'AI/R', location: 'Brazil — Remote', posted: '2026-08-19', score: 86, salary: 'Undisclosed', offer_url: 'https://www.linkedin.com/jobs/view/4452888171/', recruiter_or_careers_url: 'https://aircompany.ai/en/open-opportunities/', suggested_resume: 'Rodolfo_Rojas_React_Node_CV.pdf', strategic_note: 'Strong Node.js, React, PostgreSQL, MongoDB, APIs, architecture, AWS Lambda, distributed systems, autonomy, and AI-tool fit.',
  },
  {
    ...common,
    id: 'ruth-product-engineer-7495973496016044032', rank: 10, role: 'Senior Product Engineer', company: 'Undisclosed US education company', location: 'LATAM — Remote / Paraguay eligible', posted: '2026-08-20', score: 84, salary: 'USD 4,900–5,600/month', offer_url: 'https://www.linkedin.com/feed/update/urn:li:activity:7495973496016044032/', recruiter_or_careers_url: 'https://www.linkedin.com/in/itrecruiter-ruth-leytes/', suggested_resume: 'Rodolfo_Rojas_General_CV.pdf', strategic_note: 'React, Next.js, TypeScript, Node.js, PostgreSQL, AWS, Docker, product ownership, and AI-assisted development align, with Paraguay eligibility.',
  },
  {
    ...common,
    id: 'software-mind-744000137529619-4440337824', rank: 11, role: 'Senior Full-Stack Engineer (React + Next.js + TypeScript)', company: 'Software Mind Americas', location: 'Latin America — Remote', posted: '2026-08-06', score: 84, salary: 'Competitive USD; undisclosed', offer_url: 'https://jobs.smartrecruiters.com/SoftwareMind/744000137529619--8nw-senior-full-stack-engineer-react-next-js-typescript-', recruiter_or_careers_url: 'https://softwaremind.com/career/', suggested_resume: 'Rodolfo_Rojas_Frontend_CV.pdf', strategic_note: 'Good React, TypeScript, Next.js, Node.js, SQL, REST, consumer-product ownership, planning, code review, and cross-functional fit.',
  },
  {
    ...common,
    id: 'bc-tecnologia-63159', rank: 12, role: 'Full-Stack Developer Python Node.js', company: 'BC Tecnología', location: 'Worldwide — Fully remote', posted: '2026-08-19', score: 79, salary: 'Undisclosed', offer_url: 'https://www.getonbrd.com/empleos/programacion/full-stack-developer-python-nodejs-bc-tecnologia-santiago', recruiter_or_careers_url: 'https://www.getonbrd.com/companies/bctecnologia', suggested_resume: 'Rodolfo_Rojas_Backend_CV.pdf', strategic_note: 'Node.js, Python, REST APIs, event-driven architecture, AWS, CI/CD, and backend ownership align, with worldwide eligibility.',
  },
  {
    ...common,
    id: 'conquer-ai-4453888231', rank: 13, role: 'Software Engineer', company: 'Conquer AI', location: 'Latin America — Fully remote', posted: '2026-08-20', score: 79, salary: 'Competitive; undisclosed', offer_url: 'https://www.linkedin.com/jobs/view/4453888231/', recruiter_or_careers_url: 'https://www.linkedin.com/company/conquer-ai/life/', suggested_resume: 'Rodolfo_Rojas_React_Node_CV.pdf', strategic_note: 'The JavaScript, TypeScript or Python stack, full-stack ownership, product collaboration, code quality, mentoring, and AI-product context fit the profile.',
  },
  {
    ...common,
    id: 'xepelin-4403521647', rank: 14, role: 'Sr. Software Engineer', company: 'Xepelin', location: 'Santiago, Chile — Remote', posted: '2026-08-06', score: 78, salary: 'Undisclosed', offer_url: 'https://www.linkedin.com/jobs/view/4403521647/', recruiter_or_careers_url: 'https://www.linkedin.com/company/xepelinofficial/life/', suggested_resume: 'Rodolfo_Rojas_General_CV.pdf', strategic_note: 'System design, production ownership, cross-team architecture, mentoring, and fintech product delivery align strongly.',
  },
];

export const demoDashboard: DashboardData = {
  run: { date: '2026-08-20', timezone: 'America/Asuncion', source_file: 'job_search_2026-08-20-rerun.json' },
  summary: {
    distinct_candidates_reviewed: 122,
    passed_all_filters: 14,
    rejected_or_unverifiable: 108,
    rejection_breakdown: {
      closed_expired_or_older_than_30_days: 30,
      contract_project_or_talent_network: 20,
      hybrid_on_site_or_geography: 17,
      previously_applied_or_user_rejected: 12,
      salary_below_floor: 6,
      hard_profile_or_seniority_mismatch: 14,
      broken_login_gated_or_unverifiable: 9,
    },
  },
  jobs,
  top_three: [
    { rank: 1, company: 'Tecla', reason: 'Best current combination of exact stack, startup ownership, LATAM eligibility, full-time scope, and disclosed compensation.' },
    { rank: 2, company: 'Reap', reason: 'Strongest backend option across Node.js, NestJS, TypeScript, AWS, relational data integrity, and production reliability.' },
    { rank: 3, company: 'Deel', reason: 'Close Node.js, TypeScript, React, PostgreSQL, SaaS, microservices, and international-product fit.' },
  ],
  comparison: {
    added: ['Tecla — Sr. Full-Stack Developer'],
    retained: ['Reap', 'Deel', 'Avenue Code', 'Tecla', 'AudienceView', 'CI&T', 'Sezzle', 'AI/R', 'Software Mind Americas', 'BC Tecnología', 'Conquer AI', 'Xepelin'],
    dropped: [
      { role: 'TeamEx — Full Stack Developer — Senior', reason: 'Recorded as application_sent on 2026-08-20.' },
      { role: 'FCamara — Fullstack Node/PHP — Senior', reason: 'Recorded as application_sent on 2026-08-20.' },
    ],
  },
  issues: ['Some boards returned bot-protection or partial descriptions; every included role was independently checked on an accessible live page.'],
  blocked_sources: [{ site: 'Indeed', details: 'Indeed displayed a Security Check interstitial; no CAPTCHA bypass or repeated reload was attempted.' }],
  resume_variants: [
    { key: 'general', label: 'General Software Engineering', headline: 'Senior Software Engineer', pdf: 'Rodolfo_Rojas_General_CV.pdf' },
    { key: 'react-node', label: 'React and Node.js Full Stack', headline: 'Senior Full Stack Engineer', pdf: 'Rodolfo_Rojas_React_Node_CV.pdf' },
    { key: 'php', label: 'PHP Backend and Full Stack', headline: 'Senior PHP Engineer', pdf: 'Rodolfo_Rojas_PHP_CV.pdf' },
    { key: 'backend', label: 'Product Backend Engineering', headline: 'Senior Product Backend Engineer', pdf: 'Rodolfo_Rojas_Backend_CV.pdf' },
    { key: 'go', label: 'Go Backend Engineering', headline: 'Backend Software Engineer', pdf: 'Rodolfo_Rojas_Go_CV.pdf' },
    { key: 'frontend', label: 'Frontend Engineering', headline: 'Senior Frontend / Full Stack Engineer', pdf: 'Rodolfo_Rojas_Frontend_CV.pdf' },
  ],
};

