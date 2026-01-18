import React, { useState } from "react";
import style from "./AnalysisPage.module.css";
import { motion } from "framer-motion";
import AnalysisPageheader from "../components/AnalysisPageheader";
import Loader from "../components/Loader";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import animation from './mainpageanimation.mp4'
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
    "Food Processing",
    "Industrial Design",
    "Mechanical",
    "Metallurgy",
    "Mining",
  ];
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [File, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [positionType, setpositionType] = useState("");
  const [field, setField] = useState("");
  const [analysisResult, setAnalysisResult] = useState(""); // ✅ Add this

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleFileUpload = async () => {
    if (!File) {
      return alert("Please select your resume file.");
    }

    const formData = new FormData();
    formData.append("file", File);
    formData.append("position_type", positionType);
    formData.append("field", field);

    try {
      setLoading(true);  // Showing Loader
      const res = await axios.post("http://127.0.0.1:8000/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setAnalysisResult(res.data.result);
      navigate("/result", { state: { result: res.data.result }});
      setUploadStatus("✅ Resume analyzed successfully");
    } catch (error) {
      setUploadStatus(
        "❌ Upload failed: " + (error.response?.data?.error || "Server error")
      );
      console.error(error);
    } finally {
      setLoading(false); // Hiding the Loader
    }
  };


  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 2 }} 
      className={style.container}
    >
      <div>
        <div className={style.heading}>
          <AnalysisPageheader />
        </div>
        <div className={style.midSection}>
          <div className={style.leftSection}>
            <div className={style.inputGroup}>
              <label htmlFor="field">Choose your field:</label>
              <select
                id="field"
                className={style.dropdown}
                value={field}
                onChange={(e) => setField(e.target.value)}
              >
                <option value="">Select Field</option>
                {Fields.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>
            <div className={style.inputGroup}>
              <label htmlFor="Purpose">Purpose:</label>
              <select
                id="Purpose"
                className={style.dropdown}
                value={positionType}
                onChange={(e) => setpositionType(e.target.value)}
              >
                <option value="">Select Purpose</option>
                <option value="internship">Internship</option>
                <option value="placement">Placement</option>
              </select>
            </div>
            <div className={style.uploadGroup}>
            <label htmlFor="resumeUpload">Upload Resume:</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className={style.fileInput}
                id="resumeUpload"
              />
             
              <button onClick={handleFileUpload} className={style.uploadButton}>
                Upload Resume
              </button>
              
              {uploadStatus && <p className={style.status}>{uploadStatus}</p>}
              {loading ? (
                <Loader />
              ) :
              (
                analysisResult && (
                <div className={style.resultBox}>
                  <h3>AI Resume Feedback:</h3>
                  <pre>{analysisResult}</pre>
                </div>
              )
              )}
              
            </div>
          </div>
          <div className={style.rightSection}>
            <video
              src={animation}
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
