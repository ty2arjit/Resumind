import { Link } from 'react-router-dom';
import Wordmark from './design-system/navigation/Wordmark';

const Footer = () => {
  return (
    <footer className="border-t border-border bg-surface">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-4 px-4 py-10 text-center md:flex-row md:justify-between md:text-left">
        <Wordmark />
        <div className="flex gap-6 text-body-sm text-text-secondary">
          <Link to="/" className="hover:text-text-primary">
            Home
          </Link>
          <Link to="/contact" className="hover:text-text-primary">
            Contact Us
          </Link>
          <Link to="/help" className="hover:text-text-primary">
            Help
          </Link>
        </div>
        <p className="text-caption text-text-muted">© {new Date().getFullYear()} Resumind. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
