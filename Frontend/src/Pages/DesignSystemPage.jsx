import { FileText, Inbox, Sparkles } from 'lucide-react';
import {
  Badge,
  BaseCard,
  Button,
  Checkbox,
  EmptyState,
  ErrorState,
  EvidenceCard,
  ImportanceBadge,
  Input,
  InsightCard,
  MatchStatusBadge,
  MetricCard,
  ProgressState,
  Radio,
  RecommendationCard,
  RequirementCard,
  ScoreBadge,
  ScoreBar,
  ScoreBreakdownRow,
  ScoreCard,
  ScoreHero,
  ScoreRing,
  SearchInput,
  SectionCard,
  Select,
  SidebarNav,
  Skeleton,
  Spinner,
  Textarea,
  Toggle,
  Wordmark,
} from '../Components/design-system';

/**
 * Living showcase of every Phase 11 design-system component. Not part of
 * the product dashboard (that's Phase 12) — this page exists purely to
 * visually verify the token system and component library render
 * correctly together.
 */
export default function DesignSystemPage() {
  return (
    <div className="flex min-h-screen bg-background">
      <SidebarNav activeKey="dashboard" />
      <main className="flex-1 space-y-10 p-8">
        <header>
          <Wordmark />
          <h1 className="mt-4 text-display font-semibold text-text-primary">Design System</h1>
          <p className="mt-2 text-body-lg text-text-secondary">Refined Editorial Analytics — centralized tokens and reusable components.</p>
        </header>

        <SectionCard title="Typography">
          <div className="space-y-2">
            <p className="text-display font-bold">Display 48</p>
            <p className="text-h1 font-bold">Heading 1</p>
            <p className="text-h2 font-semibold">Heading 2</p>
            <p className="text-h3 font-semibold">Heading 3</p>
            <p className="text-h4 font-semibold">Heading 4</p>
            <p className="text-body-lg">Body large — readable paragraph copy.</p>
            <p className="text-body">Body — default UI text.</p>
            <p className="text-body-sm text-text-secondary">Body small — supporting text.</p>
            <p className="text-caption text-text-muted">Caption — metadata.</p>
            <p className="text-label font-semibold uppercase tracking-wide text-text-secondary">Label</p>
          </div>
        </SectionCard>

        <SectionCard title="Color palette">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {['primary', 'secondary', 'accent', 'success', 'warning', 'error', 'info'].map((token) => (
              <div key={token} className="rounded-md border border-border p-3">
                <div className="h-10 w-full rounded" style={{ backgroundColor: `var(--color-${token})` }} />
                <p className="mt-2 text-caption font-medium text-text-secondary">{token}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-6">
            {['very-strong', 'strong', 'partial', 'weak', 'missing', 'unknown'].map((token) => (
              <div key={token} className="rounded-md border border-border p-3">
                <div className="h-8 w-full rounded" style={{ backgroundColor: `var(--color-match-${token})` }} />
                <p className="mt-2 text-caption font-medium text-text-secondary">match-{token}</p>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Scores">
          <ScoreHero score={84} label="ATS Alignment" description="Strong alignment with the requirements of this role." />

          <div className="mt-6 max-w-md space-y-3">
            <ScoreBreakdownRow label="Required Skills" score={91} weight={28} />
            <ScoreBreakdownRow label="Responsibilities" score={82} weight={22} />
            <ScoreBreakdownRow label="Experience" score={76} weight={18} />
            <ScoreBreakdownRow label="Qualifications" score={100} weight={10} />
          </div>

          <div className="mt-6 flex flex-wrap items-end gap-8">
            <ScoreRing score={87} label="ATS Alignment" size="md" />
            <div className="flex flex-col gap-2">
              <ScoreBadge score={91} />
              <ScoreBadge score={55} />
              <ScoreBadge score={20} />
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <ScoreCard title="ATS Alignment" description="How well you match this job" score={84} />
            <ScoreCard title="Resume Quality" description="Structure & evidence" score={91} />
            <ScoreCard title="Target Fit" description="Career target alignment" score={67} />
          </div>
        </SectionCard>

        <SectionCard title="Buttons">
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="primary">Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="tertiary">Tertiary</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="primary" loading>
              Loading
            </Button>
            <Button variant="primary" disabled>
              Disabled
            </Button>
            <Button variant="primary" icon={Sparkles}>
              With icon
            </Button>
          </div>
        </SectionCard>

        <SectionCard title="Badges">
          <div className="flex flex-wrap gap-2">
            <Badge>Matched</Badge>
            <ImportanceBadge importance="REQUIRED" />
            <ImportanceBadge importance="PREFERRED" />
            <ImportanceBadge importance="OPTIONAL" />
            <MatchStatusBadge status="VERY_STRONG" />
            <MatchStatusBadge status="STRONG" />
            <MatchStatusBadge status="PARTIAL" />
            <MatchStatusBadge status="WEAK" />
            <MatchStatusBadge status="MISSING" />
            <MatchStatusBadge status="UNKNOWN" />
          </div>
        </SectionCard>

        <SectionCard title="Forms">
          <div className="grid max-w-xl grid-cols-1 gap-4 sm:grid-cols-2">
            <Input label="Position" placeholder="Backend Software Engineer" />
            <Select label="Domain" defaultValue="">
              <option value="" disabled>
                Select a domain
              </option>
              <option>FinTech</option>
              <option>HealthTech</option>
            </Select>
            <Textarea label="Notes" placeholder="Optional context..." className="sm:col-span-2" />
            <SearchInput placeholder="Search resumes..." className="sm:col-span-2" />
            <Checkbox label="Include preferred skills" defaultChecked />
            <Toggle label="Combined analysis mode" defaultChecked />
            <Radio name="mode" value="jd" label="Specific JD" defaultChecked />
            <Radio name="mode" value="target" label="Target Profile" />
            <Input label="Email" error="This field is required" className="sm:col-span-2" />
          </div>
        </SectionCard>

        <SectionCard title="Cards">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <MetricCard label="Resumes analyzed" value="128" trend={{ direction: 'up', label: '+12 this week' }} icon={FileText} />
            <InsightCard tone="positive" title="Strong required-skills coverage" description="7 of 8 required skills matched with strong evidence." />
            <RequirementCard
              text="Experience with PostgreSQL"
              category="Required Skills"
              importance="REQUIRED"
              status="VERY_STRONG"
              score={0.94}
              evidenceCount={2}
            />
            <EvidenceCard
              requirement="Experience with PostgreSQL"
              evidenceText="Optimized PostgreSQL queries and reduced latency by 35%."
              source="Experience · Backend Engineer"
              status="VERY_STRONG"
              technologies={['PostgreSQL', 'SQL']}
            />
            <RecommendationCard
              priority="CRITICAL"
              type="Address Missing Requirement"
              message="Kubernetes is a required skill that is not currently demonstrated in your resume."
              relatedRequirement="Experience with Kubernetes"
            />
            <BaseCard>
              <p className="text-body font-semibold text-text-primary">BaseCard</p>
              <p className="mt-1 text-body-sm text-text-secondary">The foundation every other card extends.</p>
            </BaseCard>
          </div>
        </SectionCard>

        <SectionCard title="Feedback states">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <EmptyState icon={Inbox} title="No analyses yet" description="Run your first analysis to see results here." action={<Button size="sm">Start analysis</Button>} />
            <ErrorState title="Analysis failed" description="We couldn't process this resume. Please try again." onRetry={() => {}} />
            <div className="flex items-center gap-6">
              <Spinner label="Loading" />
              <Skeleton className="h-4 w-32" />
            </div>
            <ProgressState
              steps={['Parsing resume...', 'Understanding job description...', 'Matching requirements...', 'Evaluating evidence...', 'Calculating ATS score...']}
              currentIndex={2}
            />
          </div>
        </SectionCard>

      </main>
    </div>
  );
}
