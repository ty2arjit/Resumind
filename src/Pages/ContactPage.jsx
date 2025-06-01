import React from "react";
import { motion } from "framer-motion";
import styles from "./ContactPage.module.css";

const Contact = () => {
  return (
    <motion.div
      className={styles.container}
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className={styles.contactBox}>
        <h2>Contact Us</h2>
        <div className={styles.infoSection}>
          <h3>Mobile Numbers</h3>
          <ul>
            <li>+91 8810811756</li>
            <li>+91 9956814867</li>
            <li>+91 9621274132</li>
            <li>+91 7985170875</li>
            <li>+91 9520230163</li>
          </ul>
        </div>
        <div className={styles.infoSection}>
          <h3>Email Addresses</h3>
          <ul>
            <li>ty2arjit@gmail.com</li>
            <li>adarsh9tiwari@gmail.com</li>
            <li>dev88tiwari@gmail.com</li>
          </ul>
        </div>
      </div>
    </motion.div>
  );
};

export default Contact;
