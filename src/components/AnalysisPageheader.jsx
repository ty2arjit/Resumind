import React from "react";
import { motion } from "framer-motion";
import style from "./AnalysisPageheader.module.css";

const AnalysisPageheader = () => {
  return (
    <motion.div
      className={style.headerContainer}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7 }}
    >
      <h1 className={style.mainHeading}>
        🎯 Welcome to <span className={style.highlight}>ResuMind</span>
      </h1>
      <p className={style.subText}>
      Make your resume <strong style={{color: "black"}}>job-ready</strong> with smart analysis, personalized suggestions, and AI-powered insights.

      </p>
    </motion.div>
  );
};

export default AnalysisPageheader;
