import React from "react";
import style from "./HighlightCards.module.css";

const data = [
  {
    title: "Smart Resume Parsing",
    desc: "Automatically extracts key details like skills, education, and experience."
  },
  {
    title: "AI-Based Scoring",
    desc: "Analyzes your resume and gives personalized feedback for improvement."
  },
  {
    title: "Job Role Matching",
    desc: "Matches your resume with relevant job roles using AI models."
  },
  {
    title: "Instant Suggestions",
    desc: "Get real-time tips on formatting, tone, and content quality."
  }

];

const HighlightCards = () => {
  return(
    <div className={style.highlightcontainer}>
      {data.map((item,idx) => (
        <div key={idx} className={style.highlightcard}>
        <h3>{item.title}</h3>
        <p>{item.desc}</p>
        </div>
      ))}
    </div>
  )
}

export default HighlightCards;