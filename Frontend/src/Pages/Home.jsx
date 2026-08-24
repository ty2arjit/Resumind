import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Check, TriangleAlert } from 'lucide-react';
import { Button, ScoreBreakdownRow, ScoreHero } from '../Components/design-system';
import HighlightCards from '../Components/HighlightCards';

/**
 * Landing page (frontendReadme §40) — the product itself is the hero:
 * a realistic analysis preview built from the real design system, not a
 * generic "AI-powered resume analyzer" gradient hero. The scores below
 * are a static illustrative preview for marketing purposes, not a live
 * API call — the actual product experience lives at /dashboard.
 */
const Home = () => {
  const navigate = useNavigate();

  return (
    <div>
      <section className="mx-auto max-w-6xl px-4 pb-20 pt-16 md:px-8 md:pb-28 md:pt-24">
        <div className="grid grid-cols-1 items-center gap-16 md:grid-cols-2">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <p className="text-label font-semibold uppercase tracking-wider text-primary">Resume Intelligence</p>
            <h1 className="mt-3 text-display font-semibold leading-[1.08] tracking-tight text-text-primary">
              Know exactly how your resume reads to an ATS.
            </h1>
            <p className="mt-5 max-w-md text-body-lg text-text-secondary">
              Resumind matches your resume against a job description requirement by requirement — showing you what's
              strong, what's missing, and the exact evidence behind every score.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button size="lg" onClick={() => navigate('/analyse')}>
                Analyze your resume
              </Button>
              <Button size="lg" variant="tertiary" onClick={() => navigate('/help')}>
                See how it works
              </Button>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="rounded-lg border border-border bg-surface p-6 shadow-medium"
          >
            <p className="text-label font-semibold uppercase tracking-wider text-text-muted">Analysis preview</p>
            <div className="mt-3">
              <ScoreHero score={84} label="ATS Alignment" description="Strong alignment with the requirements of this role." />
            </div>
            <div className="mt-6 space-y-3 border-t border-border-subtle pt-5">
              <ScoreBreakdownRow label="Required Skills" score={91} weight={28} />
              <ScoreBreakdownRow label="Responsibilities" score={82} weight={22} />
              <ScoreBreakdownRow label="Experience" score={76} weight={18} />
            </div>
            <div className="mt-5 space-y-2 border-t border-border-subtle pt-5">
              <div className="flex items-center gap-2 text-body-sm text-text-primary">
                <Check className="h-3.5 w-3.5 text-teal" strokeWidth={2.25} />
                PostgreSQL — Very Strong
              </div>
              <div className="flex items-center gap-2 text-body-sm text-text-primary">
                <TriangleAlert className="h-3.5 w-3.5 text-warning" strokeWidth={2.25} />
                Kubernetes — Missing
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="border-t border-border bg-surface-muted">
        <div className="mx-auto max-w-6xl px-4 py-16 md:px-8">
          <p className="text-label font-semibold uppercase tracking-wider text-text-muted">What you get</p>
          <h2 className="mt-2 text-h1 font-semibold text-text-primary">Explainable, requirement-level scoring.</h2>
          <div className="mt-8">
            <HighlightCards />
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
