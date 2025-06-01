import React from "react";
import { motion } from "framer-motion";
import styles from "./HelpPage.module.css";

const Help = () => {
  return (
    <motion.div
      className={styles.container}
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className={styles.helpBox}>
        <h2>Need Help?</h2>
        <p>
          We’re here to assist you! Whether you have questions about how to use the Smart Resume Analyzer, 
          want to report a bug, or need guidance on improving your resume, our support team is ready to help.
        </p>
        <p>
          Feel free to reach out anytime — your success is our priority!
        </p>
      </div>
    </motion.div>
  );
};

export default Help;
