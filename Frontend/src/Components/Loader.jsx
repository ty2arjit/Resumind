import React from "react";
import style from "./Loader.module.css";
import { motion } from "framer-motion";

const Loader = () => {
  return(
    <div className={style.loaderContainer}>
      <motion.div
      className={style.spinner}
      animate={{ rotate: 360}}
      transition={{ repeat: Infinity, duration: 1, ease: "linear"}}
      />
      <h2 className={style.loaderText}>
        Analysing your resume <span className={style.dots}></span>
      </h2>
    </div>
  )
}

export default Loader;