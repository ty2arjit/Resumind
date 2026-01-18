import React from "react";
import styles from './HighlightCards.module.css';

const features = [
  {
    title: "Smart Resume Analysis",
    description: "AI analyzes your resume contextually for structure, content, and clearity."
  },
  {
    title: "Domain-Specific Feedback",
    description: "Feedback is tailored based on your selected job domain."
  },
  {
    title: "Internship vs Placement Modes",
    description: "Different criteria for internships and placements to ensure fair evaluations. "
  },
  {
    title: "Resume Scoring System",
    description: "Get a visual score and suggestions to improve your resume instantly."
  }
];

const HighlightCards = () => {
  return (
    <div className={styles.container}>
    {features.map((feature,index) => (
      <div key={index} className={styles.card}>
      <h3>
        {feature.title}
      </h3>
      <p>
        {feature.description}
      </p>
      </div>
    ))}
    </div>
  )
}

export default HighlightCards;