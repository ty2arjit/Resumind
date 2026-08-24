import axios from 'axios';

/**
 * Thin client for the real FastAPI backend built in Phases 2-10
 * (Backend/fastapi_app/app/api/*). Every function here hits an actual
 * endpoint and returns actual backend data — no mock/fake responses.
 * Mirrors the existing app's convention (AnalysisPage.jsx) of talking to
 * FastAPI directly on :8000 during local development.
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const client = axios.create({ baseURL: BASE_URL });

export function parseResume(file) {
  const form = new FormData();
  form.append('file', file);
  return client.post('/resumes/parse', form).then((r) => r.data);
}

export function parseJobDescription({ file, text }) {
  const form = new FormData();
  if (file) form.append('file', file);
  if (text) form.append('text', text);
  return client.post('/jobs/parse', form).then((r) => r.data);
}

export function analyzeResumeQuality(file) {
  const form = new FormData();
  form.append('file', file);
  return client.post('/resume-quality', form).then((r) => r.data);
}

export function listTargetPositions() {
  return client.get('/target-profiles/positions').then((r) => r.data);
}

export function listTargetDomains() {
  return client.get('/target-profiles/domains').then((r) => r.data);
}

export function previewTargetProfile({ position, domain, customRequirements }) {
  return client
    .post('/target-profiles/preview', { position, domain: domain || null, custom_requirements: customRequirements })
    .then((r) => r.data);
}

export function analyzeTargetFit({ file, position, domain, customRequirements }) {
  const form = new FormData();
  form.append('file', file);
  form.append('position', position);
  if (domain) form.append('domain', domain);
  if (customRequirements) form.append('custom_requirements', JSON.stringify(customRequirements));
  return client.post('/target-profiles/analyze', form).then((r) => r.data);
}

export function runAnalysis({ resumeFile, jobDescriptionText, position, domain, customRequirements }) {
  const form = new FormData();
  form.append('resume_file', resumeFile);
  if (jobDescriptionText) form.append('job_description_text', jobDescriptionText);
  if (position) form.append('position', position);
  if (domain) form.append('domain', domain);
  if (customRequirements) form.append('custom_requirements', JSON.stringify(customRequirements));
  return client.post('/analysis', form).then((r) => r.data);
}

/** Normalizes an axios error into a short, non-technical message —
 * never surface a raw stack trace or backend internals (spec Phase 11 §30). */
export function toUserMessage(error) {
  const detail = error?.response?.data?.error?.message;
  if (detail) return detail;
  if (error?.request) return 'Could not reach the Resumind backend. Check that the API server is running.';
  return 'Something unexpected happened. Please try again.';
}
