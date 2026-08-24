import { motion } from 'framer-motion';
import { BaseCard, SectionCard } from '../Components/design-system';

const STEPS = [
  { title: 'Choose your field and goal', description: 'Select the field you want to apply for, and whether you are targeting an internship or a placement.' },
  { title: 'Upload your resume', description: 'Upload your current resume in PDF or DOCX format.' },
  { title: 'Get your resume analyzed', description: 'Resumind extracts the structured content of your resume and matches it against the role.' },
  { title: 'Review your report', description: 'See your score, requirement-level matches, and priority-ranked gaps to address first.' },
];

const TIPS = [
  'Keep it short and clear — ideally 1–2 pages.',
  'Use role-specific keywords and concrete achievements.',
  'Maintain a clean layout with clearly labeled sections.',
  'Quantify your work where accurate (e.g. "Reduced latency by 35%").',
];

const Help = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mx-auto max-w-3xl px-4 py-16 md:px-8"
    >
      <h1 className="text-h1 font-semibold text-text-primary">How to use Resumind</h1>
      <p className="mt-2 text-body-lg text-text-secondary">Follow these steps to get the most accurate analysis of your resume.</p>

      <div className="mt-8 space-y-3">
        {STEPS.map((step, index) => (
          <BaseCard key={step.title} className="flex flex-row items-start gap-4">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-soft-brand font-mono text-body-sm font-semibold text-primary">
              {index + 1}
            </span>
            <div>
              <h2 className="text-h4 font-semibold text-text-primary">{step.title}</h2>
              <p className="mt-1 text-body-sm text-text-secondary">{step.description}</p>
            </div>
          </BaseCard>
        ))}
      </div>

      <SectionCard title="Tips to improve your score" className="mt-8">
        <ul className="space-y-2">
          {TIPS.map((tip) => (
            <li key={tip} className="flex items-start gap-2 text-body-sm text-text-secondary">
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-text-muted" />
              {tip}
            </li>
          ))}
        </ul>
      </SectionCard>
    </motion.div>
  );
};

export default Help;
