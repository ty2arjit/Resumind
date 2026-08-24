import { motion } from 'framer-motion';
import { Mail, Phone } from 'lucide-react';
import { SectionCard } from '../Components/design-system';

const PHONE_NUMBERS = [
  '+91 8810811756',
  '+91 9956814867',
  '+91 9621274132',
  '+91 7985170875',
  '+91 9520230163',
  '+91 9073576903',
  '+91 9692369946',
];

const EMAILS = ['ty2arjit@gmail.com', 'adarsh9tiwari@gmail.com', 'dev88tiwari@gmail.com'];

const Contact = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mx-auto max-w-3xl px-4 py-16 md:px-8"
    >
      <h1 className="text-h1 font-semibold text-text-primary">Contact us</h1>
      <p className="mt-2 text-body-lg text-text-secondary">Reach out with questions, feedback, or support requests.</p>

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <SectionCard
          title="Phone"
          action={<Phone className="h-5 w-5 text-text-muted" strokeWidth={1.75} />}
        >
          <ul className="space-y-1.5 font-mono text-body-sm text-text-secondary">
            {PHONE_NUMBERS.map((number) => (
              <li key={number}>{number}</li>
            ))}
          </ul>
        </SectionCard>

        <SectionCard
          title="Email"
          action={<Mail className="h-5 w-5 text-text-muted" strokeWidth={1.75} />}
        >
          <ul className="space-y-1.5 text-body-sm text-text-secondary">
            {EMAILS.map((email) => (
              <li key={email}>{email}</li>
            ))}
          </ul>
        </SectionCard>
      </div>
    </motion.div>
  );
};

export default Contact;
