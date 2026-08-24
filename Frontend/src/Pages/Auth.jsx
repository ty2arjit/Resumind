import { useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Button, ErrorState, Input } from '../Components/design-system';
import Wordmark from '../Components/design-system/navigation/Wordmark';

const Auth = ({ setAuthenticated }) => {
  const [isSignUp, setIsSignUp] = useState(true);
  const [form, setForm] = useState({ name: '', college: '', email: '', password: '' });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const endpoint = isSignUp ? 'signup' : 'login';
    const payload = isSignUp ? form : { email: form.email, password: form.password };

    try {
      const res = await axios.post(`http://localhost:3000/auth/${endpoint}`, payload);

      if (res.data.success) {
        if (!isSignUp) {
          const { jwtToken, email, name } = res.data;
          localStorage.setItem('resumindUser', JSON.stringify({ email, name }));
          localStorage.setItem('resumindToken', jwtToken);
          setAuthenticated(true);
          navigate('/dashboard');
        } else {
          navigate('/auth');
          setIsSignUp(false);
        }
      }
    } catch (err) {
      setError(err.response?.data?.message || `${isSignUp ? 'Signup' : 'Login'} failed`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-64px)] items-center justify-center bg-background px-4 py-16">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-sm rounded-lg border border-border bg-surface p-8 shadow-medium"
      >
        <Wordmark />
        <h1 className="mt-6 text-h2 font-semibold text-text-primary">{isSignUp ? 'Create your account' : 'Welcome back'}</h1>
        <p className="mt-1 text-body-sm text-text-secondary">
          {isSignUp ? 'Sign up to start analyzing your resume.' : 'Sign in to continue.'}
        </p>

        <form className="mt-6 flex flex-col gap-4" onSubmit={handleSubmit}>
          {isSignUp && (
            <>
              <Input label="Name" name="name" value={form.name} onChange={handleChange} required />
              <Input label="College" name="college" value={form.college} onChange={handleChange} required />
            </>
          )}
          <Input label="Email" type="email" name="email" value={form.email} onChange={handleChange} required />
          <Input label="Password" type="password" name="password" value={form.password} onChange={handleChange} required />

          {error && <ErrorState title={isSignUp ? 'Sign up failed' : 'Sign in failed'} description={error} className="!py-4" />}

          <Button type="submit" size="lg" loading={submitting} className="mt-2 w-full">
            {isSignUp ? 'Create account' : 'Log in'}
          </Button>
        </form>

        <p className="mt-6 text-center text-body-sm text-text-secondary">
          {isSignUp ? 'Already registered? ' : "Don't have an account? "}
          <button
            type="button"
            onClick={() => setIsSignUp(!isSignUp)}
            className="font-medium text-primary hover:text-primary-hover"
          >
            {isSignUp ? 'Sign in' : 'Sign up'}
          </button>
        </p>
      </motion.div>
    </div>
  );
};

export default Auth;
