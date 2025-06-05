import React from "react";
import style from "./AnalysisPage.module.css";
import { motion } from "framer-motion";
import AnalysisPageheader from "../components/AnalysisPageheader";
import photo from "./analysispageimage.png";
const MainPage = () => {
  const Fields = [
    "Software/IT",
    "Analytics",
    "VLSI",
    "Biomedical",
    "Biotechnology",
    "Chemical",
    "Civil",
    "Ceramic",
    "Electrical",
    ,
    "Food Processing",
    "Mechanical",
    "Metallurgy",
    "Mining",
    "Industrial Design",
  ];
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ durantion: 2 }}
      /*className={style.container}*/
    >
      <div /*className={style.content}*/>
        <div className={style.heading}>
          <AnalysisPageheader />
        </div>
        <div className={style.midSection}>
          <div className={style.leftSection}>
            <div className={style.inputGroup}>
              <label>Choose your field:</label>
              <select className={style.dropdown}>
                <option value="Field">Select Field</option>
                {Fields.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>
            <div className={style.inputGroup}>
              <label>Purpose:</label>
              <select className={style.dropdown}>
                <option value="Purpose">Select Purpose</option>
                <option value="internship">Internship</option>
                <option value="placement">Placement</option>
              </select>
            </div>
            <button className={style.uploadButton}>Upload Resume</button>
          </div>
          <div className={style.rightSection}>
            <video
              src="/assets/mainpageanimation.mp4"
              autoPlay
              loop
              muted
              playsInline
              className={style.video}
            ></video>
          </div>
        </div>
        <div className={style.afterMidSection}>
          <h2>What Happens After You Upload?</h2>
          <p>
            Our Smart Resume Analyzer evaluates your resume using advanced AI
            models to provide:
          </p>
          <ul>
            <li>✔ Resume Score & ATS Compatibility</li>
            <li>✔ Field-specific Skill Match Analysis</li>
            <li>✔ Improvement Suggestions Powered by AI</li>
          </ul>
          <p>
            Start your journey to building a stronger, more impactful resume
            today!
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default MainPage;
