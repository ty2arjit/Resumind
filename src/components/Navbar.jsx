import React, { useState } from "react";
import styles from "./Navbar.module.css";
import logo from "./Resume_Analyzer_logo_3.png";
import { HiUser } from "react-icons/hi";
import { Link } from "react-router-dom";

function Navbar({ isAuthenticated, setAuthenticated }) {
  const [activeId, setActiveId] = useState(null);

  const handleClick = (id) => {
    setActiveId(id);
  };
  const handleLogout = () => {
    setAuthenticated(false);
    alert("Logged out successfully!");
  }

  const NavItems = [
    { id: 1, name: "Home", href: "/" },
    { id: 2, name: "Contact Us", href: "/contact" },
    { id: 3, name: "Help", href: "/help" },
  ];

  return (
    <nav className={styles.bar}>
      <div className={styles.leftSection}>
        <img src={logo} alt="Resume Logo" className={styles.logo} />
        <ul className={styles.navList}>
          {NavItems.map((item) => (
            <li
              key={item.id}
              className={`${styles.navItem} ${activeId === item.id ? styles.active : ""}`}
              onClick={() => handleClick(item.id)}
            >
              <Link to={item.href} className={styles.link}>
                {item.name}
              </Link>
            </li>
          ))}
        </ul>
      </div>
      <div className={styles.rightSection}>
        <ul className={styles.navList}>
          <li
            className={`${styles.navItem} ${activeId === 4 ? styles.active : ""}`}
            onClick={() => handleClick(4)}
          >
            <Link to="/profile" className={styles.link}>
            <HiUser />
            </Link>
          </li>
          {/* Login/Logout button */}
          <li className={styles.navItem}>
            {isAuthenticated ? (
              <button onClick={handleLogout} className={styles.link}>Logout</button>
            ) : (
              <Link to="/auth" className={styles.link}>Login</Link>
            )}
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
