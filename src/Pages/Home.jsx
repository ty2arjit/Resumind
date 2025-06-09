import React from "react";
import { motion } from "framer-motion";
import styles from "./Home.module.css";
import HighlightCards from "../components/HighlightCards";
import { useNavigate } from "react-router-dom";
const Home = () => {
  const navigate = useNavigate();
  const handleOnClick = () => {
    navigate("/analyse");
  };
  return (
    <>
      <div>
        <motion.div
          className={styles.container}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 2 }}
        >
          <div className={styles.hero}>
            {/* Left Section: Text */}
            <motion.div
              initial={{ opacity: 0, y: 50 }} // start 50px below and invisible
              animate={{ opacity: 1, y: 0 }} // animate to fully visible and original position
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="space-y-6"
            >
              <div className={styles.textSection}>
                <h1>
                  Welcome to <span>Resumind</span>
                </h1>
                <h1>
                  Analyze your resume using <br /> AI instantly.
                  <br />
                  Get personalized feedback,
                  <br /> improvement tips,
                  <br /> and track your job readiness <br />— all in one place.
                </h1>
                <button onClick={handleOnClick} className={styles.cta}>
                  Analyze Now
                </button>
              </div>
            </motion.div>

            {/* Right Section */}
            <div className={styles.videoSection}>
              <video
                src="/assets/resume-animation.mp4"
                autoPlay
                loop
                muted
                playsInline
                className={styles.video}
              ></video>
            </div>
          </div>
        </motion.div>
      </div>
      <div>
        <HighlightCards></HighlightCards>
      </div>
    </>
  );
};

export default Home;
