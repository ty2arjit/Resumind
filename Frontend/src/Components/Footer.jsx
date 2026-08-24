import React from "react";
import styles from './Footer.module.css';
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <h2 className={styles.logo}>Resumind</h2>
      <div className={styles.link}>
        <Link to="/" className={styles.links}>Home</Link>
        <Link to="/contact" className={styles.links}>Contact Us</Link>
        <Link to="/help" className={styles.links}>Help</Link>
      </div>
      <p className={styles.copy}>© {new Date().getFullYear()} Resumind. All rights reserved.</p>
    </footer>
  );
};

export default Footer;
