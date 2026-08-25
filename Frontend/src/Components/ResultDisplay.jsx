import { lazy, Suspense } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Lightbulb } from 'lucide-react';
import { Accordion, AccordionItem, ColorimetricBar, ColorimetricMeter, Reveal, SectionCard } from './design-system';
import { colorimetricColor } from '../lib/colorimetric';
import { parseGeminiResult } from '../lib/parseGeminiResult';

const ResultOrb = lazy(() => import('./three/ResultOrb'));

/**
 * The legacy Gemini analysis result, redesigned for a student audience
 * (per user request): a colorimetric score meter instead of a plain
 * number, a section-wise score breakdown, section-by-section analysis
 * as an expandable accordion instead of a wall of paragraphs, and
 * suggestions/critical-errors as clearly color-coded cards. Parses the
 * real response shape via lib/parseGeminiResult.js — nothing here is
 * invented or re-sent to an LLM.
 */
const ResultDisplay = ({ resultText }) => {
  if (!resultText) return null;

  const parsed = parseGeminiResult(resultText);
  const { overallScore, sections, scores, suggestions, criticalErrors } = parsed;
  const meterColor = colorimetricColor(overallScore ?? 0);

  return (
    <div className="space-y-8">
      <SectionCard className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -z-10 opacity-70">
          <Suspense fallback={null}>
            <ResultOrb score={overallScore ?? 0} className="h-full w-full" />
          </Suspense>
        </div>
        <div className="flex flex-col items-center gap-2 py-4 text-center">
          <p className="text-label font-semibold uppercase tracking-wider text-text-muted">Overall Score</p>
          <ColorimetricMeter score={overallScore ?? 0} />
        </div>
      </SectionCard>

      {scores.length > 0 && (
        <Reveal>
          <SectionCard title="Score breakdown" description="How each section of your resume contributed to the total.">
            <div className="space-y-3">
              {scores.map((s) => (
                <ColorimetricBar key={s.label} label={s.label} value={s.value} max={s.max} />
              ))}
            </div>
          </SectionCard>
        </Reveal>
      )}

      {sections.length > 0 && (
        <Reveal delay={0.05}>
          <SectionCard title="Section-by-section analysis" description="Tap a section to read the full assessment.">
            <Accordion>
              {sections.map((s, i) => (
                <AccordionItem key={i} badge={s.letter} badgeColor={meterColor} title={s.title} defaultOpen={i === 0}>
                  {s.body}
                </AccordionItem>
              ))}
            </Accordion>
          </SectionCard>
        </Reveal>
      )}

      {suggestions.length > 0 && (
        <Reveal delay={0.1}>
          <SectionCard title="Personalized suggestions" description="Where to focus next to raise your score.">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {suggestions.map((s, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.06 }}
                  className="rounded-lg border border-border bg-surface p-4"
                  style={{ borderTop: '2px solid var(--color-teal)' }}
                >
                  <div className="flex items-start gap-2.5">
                    <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-teal" strokeWidth={2} />
                    <div>
                      {s.title && <p className="text-body-sm font-semibold text-text-primary">{s.title}</p>}
                      <p className="mt-0.5 text-body-sm text-text-secondary">{s.body}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </SectionCard>
        </Reveal>
      )}

      {criticalErrors.length > 0 && (
        <Reveal delay={0.15}>
          <SectionCard title="Critical errors" description="Fix these first — they carry the most weight.">
            <div className="space-y-3">
              {criticalErrors.map((e, i) => (
                <div key={i} className="rounded-lg border border-error/25 bg-error-surface p-4">
                  <div className="flex items-start gap-2.5">
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-error" strokeWidth={2} />
                    <div>
                      {e.title && <p className="text-body-sm font-semibold text-text-primary">{e.title}</p>}
                      <p className="mt-0.5 text-body-sm text-text-secondary">{e.body}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </Reveal>
      )}
    </div>
  );
};

export default ResultDisplay;
