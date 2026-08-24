import { BarChart3, FileSearch, ListChecks, Target } from 'lucide-react';
import { BaseCard } from './design-system';

const features = [
  {
    icon: FileSearch,
    title: 'Requirement-level matching',
    description: 'Every skill and responsibility in the job description is matched against specific evidence in your resume.',
  },
  {
    icon: Target,
    title: 'Target Profile fit',
    description: "No job description yet? Benchmark your resume against a position and domain instead — e.g. Backend Engineer, FinTech.",
  },
  {
    icon: ListChecks,
    title: 'Resume Quality scoring',
    description: 'A separate, structure-and-evidence score — independent of any specific job — covering parseability, dates, and content density.',
  },
  {
    icon: BarChart3,
    title: 'Priority-ranked gaps',
    description: 'Missing and partial requirements are ranked by how much they affect your score, so you know what to fix first.',
  },
];

const HighlightCards = () => {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {features.map((feature) => (
        <BaseCard key={feature.title} hoverable>
          <span className="inline-flex rounded-md bg-soft-brand p-2 text-primary">
            <feature.icon className="h-5 w-5" strokeWidth={1.75} aria-hidden="true" />
          </span>
          <h3 className="mt-4 text-h4 font-semibold text-text-primary">{feature.title}</h3>
          <p className="mt-1.5 text-body-sm text-text-secondary">{feature.description}</p>
        </BaseCard>
      ))}
    </div>
  );
};

export default HighlightCards;
