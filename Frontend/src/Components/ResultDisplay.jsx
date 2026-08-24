import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { ScoreHero, SectionCard } from './design-system';

const wrapLine = (text, wordLimit = 15) => {
  const words = text.split(' ');
  const lines = [];
  for (let i = 0; i < words.length; i += wordLimit) {
    lines.push(words.slice(i, i + wordLimit).join(' '));
  }
  return lines;
};

const ResultDisplay = ({ resultText }) => {
  if (!resultText) return null;

  const cleanedText = resultText
    .replace(/\*+/g, '')
    .replace(/\s{2,}/g, ' ')
    .replace(/(?<=\.)\s/g, '\n')
    .trim();

  const lines = cleanedText.split('\n').filter((line) => line.trim() !== '');

  const getScore = () => {
    const scoreLine = lines.find((line) => line.includes('Overall Score'));
    return parseInt(scoreLine?.match(/\d+/)?.[0]) || 0;
  };

  const overallScore = getScore();

  // Group lines into sections so each renders as one card instead of a
  // continuous scroll of individually-bordered lines.
  const sections = [];
  let current = { heading: null, points: [] };
  for (const line of lines) {
    const isSectionHeader = /^[0-9]+\.\s|^[A-G]\)/.test(line);
    const isSpecialHeading = /Final Suggestions|Field-Specific Insights/i.test(line);
    if (line.includes('Overall Score')) continue;
    if (isSectionHeader || isSpecialHeading) {
      if (current.heading || current.points.length) sections.push(current);
      current = { heading: line.trim(), points: [] };
    } else {
      current.points.push(...wrapLine(line));
    }
  }
  if (current.heading || current.points.length) sections.push(current);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} className="space-y-6">
      <SectionCard>
        <ScoreHero score={overallScore} label="Overall Score" />
      </SectionCard>

      {sections.map((section, i) => (
        <SectionCard key={i} title={section.heading ?? undefined}>
          <ul className="space-y-2">
            {section.points.map((point, j) => (
              <li key={j} className="flex items-start gap-2 text-body-sm text-text-primary">
                {j === 0 && <Check className="mt-0.5 h-4 w-4 shrink-0 text-teal" strokeWidth={2} />}
                <span className={j === 0 ? '' : 'pl-6'}>{point}</span>
              </li>
            ))}
          </ul>
        </SectionCard>
      ))}
    </motion.div>
  );
};

export default ResultDisplay;
