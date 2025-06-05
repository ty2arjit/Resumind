import React from "react";
import style from "./ContactPage.module.css";
import {motion} from "framer-motion";
import { FaPhoneAlt } from "react-icons/fa";
import { FaEnvelope } from "react-icons/fa";

const Phones = [
  "+91 9956814867",
  "+91 9621274132",
  "+91 7985170875",
  "+91 9520230163",
  "+91 8810811756",
  "+91 9073576903",
  "+91 9692369946"
];
const Emails = [
  "ty2arjit@gmail.com",
  "adarsh9tiwari@gmail.com",
  "dev88tiwari@gmail.com",
];

const Contact = () => {
  return (
    <motion.div
      className={style.wrapper}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 2 }}
    >
      <div className={style.card}>
        <h2 className={style.heading}>Contact Us</h2>
        <p className={style.subtext}>
          We're just a call or mail away. Reach out to us and we'll be happy to
          help.
        </p>
        <div className={style.section}>
        <h3 className={style.title}><FaPhoneAlt /></h3>
        <ul className={style.list}>
          {Phones.map((item,idx) => (
            <li key={idx} className={style.listitem}>{item}</li>
          ))}
        </ul>
        </div>
        <div className={style.section}>
        <h3 className={style.title}><FaEnvelope /></h3>
        <ul className={style.list}>
          {Emails.map((item,idx) => (
            <li key={idx} className={style.listitem}>{item}</li>
          ))}
        </ul>
        </div>
      </div>
    </motion.div>
  );
};

export default Contact;
