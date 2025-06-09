import React, { useState } from "react";
import styles from "./Auth.module.css";
import { motion} from "framer-motion";
const Auth = ({ setAuthenticated }) => {
  const [isSignUp, setIsSignUp] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    setAuthenticated(true);
    alert(isSignUp ? "Signed up successfully!" : "Logged in successfully!");
  }

  return (
    <motion.div
     initial = {{ opacity: 0, y:30}}
     animate = {{ opacity : 1, y: 0}}
     transition= {{duration : 2}}
    className={styles.container}>
      <div className={styles.authBox}>
        <h2>{isSignUp ? "Sign Up" : "Sign In"}</h2>
        <form className={styles.form} onSubmit={handleSubmit}>
          {isSignUp && (
            <input
              type="text"
              placeholder="Name"
              required
              className={styles.input}
            />
          )}
          <input
            type="email"
            placeholder="Email"
            required
            className={styles.input}
          />
          <input
            type="password"
            placeholder="Password"
            required
            className={styles.input}
          />
          <button type="submit" className={styles.button}>
            {isSignUp ? "Create Account" : "Log In"}
          </button>
        </form>
        <p className={styles.toggleMsg}>
          {isSignUp
            ? "Already registered? "
            : "Don't have an account? "}
          <span
            className={styles.toggleLink}
            onClick={() => setIsSignUp(!isSignUp)}
          >
            {isSignUp ? "Sign In" : "Sign Up"}
          </span>
        </p>
      </div>
    </motion.div>
  );
};

export default Auth;
