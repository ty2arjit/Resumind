import React from "react";
import { motion } from "framer-motion";
import styles from "./ContactPage.module.css";

const Contact = () => {
  return (
    <motion.div
      className={styles.wrapper}
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className={styles.card}>
        <h2 className={styles.heading}>Contact Us</h2>
        <div className={styles.section}>
          <h3 className={styles.title}>Mobile Numbers</h3>
          <ul className={styles.list}>
            <li className={styles.listitem}>+91 8810811756</li>
            <li className={styles.listitem}>+91 9956814867</li>
            <li className={styles.listitem}>+91 9621274132</li>
            <li className={styles.listitem}>+91 7985170875</li>
            <li className={styles.listitem}>+91 9520230163</li>
            <li className={styles.listitem}>+91 9073576903</li>
            <li className={styles.listitem}>+91 9692369946</li>
          </ul>
        </div>
        <div className={styles.section}>
          <h3 className={styles.title}>Email Addresses</h3>
          <ul className={styles.list}>
            <li className={styles.listitem}>ty2arjit@gmail.com</li>
            <li className={styles.listitem}>adarsh9tiwari@gmail.com</li>
            <li className={styles.listitem}>dev88tiwari@gmail.com</li>
          </ul>
        </div>
      </div>
    </motion.div>
  );
};

export default Contact;
