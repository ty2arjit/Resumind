// HelpPage.jsx
import React from "react";
import style from "./HelpPage.module.css";
import { motion } from "framer-motion";

const Help = () => {
  return (
    <motion.div
      className={style.wrapper}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1 }}
    >
      <div className={style.card}>
        <h1 className={style.heading}>How to Use Resumind</h1>
        <h3 className={style.intro}>
          Follow these simple steps to get the most accurate resume analysis and
          boost your placement/internship chances!
        </h3>

        <motion.div
          className={style.step}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1}}
        >
          <h2>Step 1: Choose your Field</h2>
          <h3>
             Select the field in which you want to apply for.
          </h3>
          <h2>Step 2: Choose Your Goal</h2>
          <h3>
            Select Internship or Placement to help us personalize your resume
            feedback.
          </h3>
        </motion.div>

        <motion.div
          className={style.step}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 2 }}
        >
          <h2>Step 3: Upload Your Resume</h2>
          <h3>
            Upload your updated resume in PDF/DOCX format for accurate analysis.
          </h3>
        </motion.div>

        <motion.div
          className={style.step}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 3 }}
        >
          <h2>Step 4: Get Your Resume Analyzed</h2>
          <h3>
            Our AI engine extracts key insights and gives you a detailed score
            report.
          </h3>
        </motion.div>

        <motion.div
          className={style.step}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 4}}
        >
          <h2>Step 5: Review Your Report</h2>
          <h3>
            Understand strengths, weaknesses, and get improvement suggestions
            instantly.
          </h3>
        </motion.div>

        <motion.div
          className={style.tips}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 5 }}
        >
          <h2>Tips to Improve Your Resume Score</h2>
          <ul>
            <li><h3>Keep it short and clear – ideally 1–2 pages.</h3></li>
            <li><h3>Use job-specific keywords and achievements.</h3></li>
            <li><h3>Maintain a clean layout with sections.</h3></li>
            <li><h3>Quantify your work (e.g., "Increased sales by 20%").</h3></li>
          </ul>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default Help;
