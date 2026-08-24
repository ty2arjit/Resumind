import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Check } from 'lucide-react';
import AnalysisPageheader from '../Components/AnalysisPageheader';
import Loader from '../Components/Loader';
import { Button, ErrorState, FileUpload, SectionCard, Select } from '../Components/design-system';
import animation from './mainpageanimation.mp4';

const FIELDS = [
  'Software/IT', 'Analytics', 'VLSI', 'Biomedical', 'Biotechnology', 'Chemical', 'Civil', 'Ceramic',
  'Electrical', 'Electronics & Communication', 'Electronics & Instrumentation', 'Food Processing',
  'Industrial Design', 'Mechanical', 'Metallurgy', 'Mining',
];

const MainPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [positionType, setPositionType] = useState('');
  const [field, setField] = useState('');

  const handleFileUpload = async () => {
    if (!file) return setError('Please select your resume file.');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('position_type', positionType);
    formData.append('field', field);

    setError(null);
    setLoading(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      navigate('/result', { state: { result: res.data.result } });
    } catch (err) {
      setError(err.response?.data?.error || 'Server error — please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mx-auto max-w-6xl px-4 py-16 md:px-8"
    >
      <AnalysisPageheader />

      <div className="mt-10 grid grid-cols-1 gap-8 lg:grid-cols-2">
        <SectionCard title="Upload your resume">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Select label="Field" value={field} onChange={(e) => setField(e.target.value)}>
              <option value="">Select field</option>
              {FIELDS.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </Select>
            <Select label="Purpose" value={positionType} onChange={(e) => setPositionType(e.target.value)}>
              <option value="">Select purpose</option>
              <option value="Intern">Internship</option>
              <option value="Placement">Placement</option>
            </Select>
          </div>

          <FileUpload
            label="Resume file"
            helperText="PDF only"
            accept=".pdf"
            fileName={file?.name}
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="mt-4"
          />

          <Button onClick={handleFileUpload} disabled={loading} loading={loading} className="mt-5 w-full" size="lg">
            {loading ? 'Analyzing...' : 'Upload and analyze'}
          </Button>

          {loading && <Loader />}
          {error && <ErrorState className="mt-4" title="Analysis failed" description={error} />}
        </SectionCard>

        <div className="overflow-hidden rounded-lg border border-border bg-surface-muted">
          <video src={animation} autoPlay loop muted playsInline className="h-full w-full object-cover" />
        </div>
      </div>

      <SectionCard title="What happens after you upload?" className="mt-8">
        <p className="text-body-sm text-text-secondary">Resumind evaluates your resume to provide:</p>
        <ul className="mt-3 space-y-2">
          {['Resume score & ATS compatibility', 'Field-specific skill match analysis', 'Concrete improvement suggestions'].map((item) => (
            <li key={item} className="flex items-center gap-2 text-body-sm text-text-primary">
              <Check className="h-4 w-4 text-teal" strokeWidth={2} />
              {item}
            </li>
          ))}
        </ul>
      </SectionCard>
    </motion.div>
  );
};

export default MainPage;
