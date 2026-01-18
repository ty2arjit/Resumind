import React from "react";
import { motion } from "framer-motion";
import styles from "./Home.module.css";
import HighlightCards from "../components/HighlightCards";
import { useNavigate } from "react-router-dom";
import video from './resume-animation.mp4';
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
                <p>
                  <span>Resumind</span>
                </p>
                <h1>
                  You’ve Done the Hard Work.
                  <br />
                  We’ll Help You Present It Right.
                  <br />
                </h1>

                <h3>
                  Resumind gives your resume the AI treatment <br />
                  —Upload it to Resumind and get instant,
                  <br />
                  AI driven feedback crafted to help you stand out <br />
                  — whether you're aiming for an internship, <br />
                  job switch, or your first big break.
                </h3>

                <button onClick={handleOnClick} className={styles.cta}>
                  Analyze Now
                </button>
              </div>
            </motion.div>

            {/* Right Section */}
            <div className={styles.videoSection}>
              <video
                src={video}
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
