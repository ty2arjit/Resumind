import React from "react";
import style from "./Footer.module.css";
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className={style.footer}>
    <div className={style.footerContent}>
      <div className={style.brand}>
        <h2>Resumind</h2>
        <p>Your smart resume assistant</p>
      </div>
      <div className={style.links}>
      <Link to="/">Home</Link>
      <Link to="/contact">Contact</Link>
      <Link to="/help">Help</Link>
      <Link to="/profile">Profile</Link>
      </div>
      <div className={style.copy}>
      © {new Date().getFullYear()} Resumind. All rights reserved.
      </div>
    </div>
    </footer>
  )
}

export default Footer;