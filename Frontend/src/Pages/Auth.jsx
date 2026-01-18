import React, { useState } from "react";
import styles from "./Auth.module.css";
import { motion } from "framer-motion";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Auth = ({ setAuthenticated }) => {
  const [isSignUp, setIsSignUp] = useState(true);
  const [form, setForm] = useState({
    name: "",
    college: "",
    email: "",
    password: ""
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
  
    const endpoint = isSignUp ? "signup" : "signin";
    const payload = isSignUp
      ? form
      : { email: form.email, password: form.password };
  
    try {
      const res = await axios.post(`http://127.0.0.1:8000/api/auth/${endpoint}`, payload);
      
      if (res.status === 200 || res.status === 201) {
        const { user, token } = res.data;
  
        // 🔐 Store in localStorage
        localStorage.setItem("resumindUser", JSON.stringify(user));
        localStorage.setItem("resumindToken", token);
  
        setAuthenticated(true);
        alert(isSignUp ? "Signed up successfully!" : "Logged in successfully!");
        navigate("/");
      }
    } catch (err) {
      console.error("Axios error:", err);
      alert(err.response?.data?.error || `${isSignUp ? "Signup" : "Signin"} failed`);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1.5 }}
      className={styles.container}
    >
      <div className={styles.authBox}>
        <h2>{isSignUp ? "Sign Up" : "Sign In"}</h2>
        <form className={styles.form} onSubmit={handleSubmit}>
          {isSignUp && (
            <>
              <input
                type="text"
                name="name"
                placeholder="Name"
                value={form.name}
                onChange={handleChange}
                required
                className={styles.input}
              />
              <input
                type="text"
                name="college"
                placeholder="College"
                value={form.college}
                onChange={handleChange}
                required
                className={styles.input}
              />
            </>
          )}
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            required
            className={styles.input}
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            required
            className={styles.input}
          />
          <button type="submit" className={styles.button}>
            {isSignUp ? "Create Account" : "Log In"}
          </button>
        </form>
        <p className={styles.toggleMsg}>
          {isSignUp ? "Already registered? " : "Don't have an account? "}
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
