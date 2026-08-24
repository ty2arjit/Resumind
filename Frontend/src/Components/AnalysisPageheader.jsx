import React from "react";
import styles from "./AnalysisPageheader.module.css";

const AnalysisPageheader = () => {
  return (
    <div className={styles.headerContainer}>
      <h1 className={styles.heading}>
      <span className={styles.emoji}>🎯</span> Welcome to <span className={styles.Resumind}>Resumind</span>
      </h1>
      <p className={styles.subheading}>
        Make your resume job-ready with AI-powered analysis tailored to your
        goals.
      </p>
    </div>
  );
};

export default AnalysisPageheader;
