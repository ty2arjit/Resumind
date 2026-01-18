import css from "./Result.module.css";
import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import ResultDisplay from "../components/ResultDisplay";
const ResultPage = () => {
  const { state } = useLocation();
  const navigate = useNavigate();
  const result = state?.result;

  if (!result) {
    <div className={css.noData}>
      <h2>No analysis data found</h2>
      <button onClick={() => navigate("/analyse")}>Go Back</button>
    </div>;
  }

  console.log("State result:", result);


  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1.2 }}
      className={css.page}
    >
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1.2 }}
        className={css.wrapper}
      >
      {/*
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2 }}
          className={css.firstcontainer}
        >
        </motion.div>*/}
      
      <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1.2 }}
          >
            {/*<h1 className={css.header}>📊 Your Resume Analysis:</h1>*/}
            <div>
              <ResultDisplay resultText={result} />
            </div>
            <button
              onClick={() => navigate("/analyse")}
              className={css.backButton}
            >
              Analyse Another Resume
            </button>
          </motion.div>
          </motion.div>
    </motion.div>
  );
};

export default ResultPage;
