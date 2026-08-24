import { motion } from 'framer-motion';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button, EmptyState } from '../Components/design-system';
import ResultDisplay from '../Components/ResultDisplay';

const ResultPage = () => {
  const { state } = useLocation();
  const navigate = useNavigate();
  const result = state?.result;

  if (!result) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 md:px-8">
        <EmptyState
          title="No analysis data found"
          description="Analyze a resume first to see your results here."
          action={<Button onClick={() => navigate('/analyse')}>Analyze a resume</Button>}
        />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mx-auto max-w-3xl px-4 py-16 md:px-8"
    >
      <ResultDisplay resultText={result} />
      <Button variant="secondary" size="lg" onClick={() => navigate('/analyse')} className="mt-8">
        Analyze another resume
      </Button>
    </motion.div>
  );
};

export default ResultPage;
