import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_CSE_Placement(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Computer Science Engineering placements**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

Your evaluation must include the following:

---

### A) SECTION-BY-SECTION ANALYSIS  
Analyze the following resume sections using capital letters in the format (A), (B), (C)...  
**Do NOT use numbered sections. Do NOT use full stops after section headings. Leave a space and then start the analysis.**

#### Sections to Analyze:
- Contact Information  
- Summary/Objective (if present)  
- Education  
- Relevant Coursework  
- Projects  
- Technical Skills  
- Work Experience (if any)  
- Certifications / Achievements  
- Extra-curricular Activities  
- Formatting & ATS Compatibility  
- Give overall score as the sum of marks obtained in each section.

---

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for CSE Placement)

✅ **CSE Placement Guidelines:**
- Prioritize core CS subjects: **Data Structures, Algorithms, OOP, DBMS, OS, CN, Computer Architecture**
- Reward experience with **real-world projects, internships, live product deployments**
- Reward advanced tech: **MERN, DevOps, Docker, CI/CD, Cloud (AWS/GCP), Microservices, ML/DL**
- Reward GitHub repos, LinkedIn, portfolios with live demos
- Reward achievements in **coding contests (Codeforces, CodeChef, LeetCode)** or **open source**
- Penalize repetitive projects, missing links, unquantified work
- Emphasize clean bullet points with **action verbs + metrics**

---

### C) GRADING SYSTEM (Total: 100 marks)

Each section contributes specific marks:

- **Education** (10 marks)  
  - +5 for CGPA/percentage  
  - +1 for school/college names  
  - +2 for years of 10th & 12th  
  - +2 if board names are given  
  - -2 for any formatting or clarity issues  

- **Relevant Coursework** (10 marks)  
  - +8 for CS core subjects  
  - +2 for electives like AI, Cloud, Cybersecurity, Software Engineering  
  - -2 for missing/poorly formatted courses  

- **Projects** (20 marks)  
  - +5 for each project (max 2) with proper description, stack, and output  
  - +3 for deployment (e.g., Vercel, Heroku, Firebase)  
  - +4 for advanced features, real user base  
  - -2 for poor grammar, no links, or vague bullets  

- **Technical Skills** (20 marks)  
  - Reward structure: Languages, Frameworks, Tools  
  - Penalize generic lists or keyword stuffing  
  - +3 for categorized, ATS-optimized formatting  

- **Work Experience / Internships** (10 marks)  
  - +10 for real tech internships with product/feature contribution  
  - +5 for training or freelance work  
  - -2 for filler points or non-CS roles  

- **Achievements & Certifications** (10 marks)  
  - +5 for CP performance, Kaggle/ML, or Hackathons  
  - +5 for recognized certifications (GCP, AWS, Meta, IBM, Coursera, etc.)  
  - Score based on real value & difficulty  

- **Extra-curricular Activities** (10 marks)  
  - Reward GDSC, IEEE, developer clubs, leadership, events  
  - Penalize irrelevant or filler items  

- **Contact Info + ATS Formatting** (5 marks)  
  - +5 for phone, email, LinkedIn, GitHub/portfolio present  
  - -2 for missing one  
  - -3 for poor formatting (multi-column, table layouts)

- **Writing, Grammar, Metrics** (5 marks)  
  - +5 for use of action verbs, numbers, clean structure  
  - -1 per spelling/grammar error

---

### D) #FINAL OUTPUT

#At the end of your analysis, **return the following**:

-Don't use integers to start a line/heading or use without full stop because the line breaks after full stop in our UI so I don't want a full stop in between the heading and starting number.  
-Overall Score = XX/100. (XX is the sum of scores in each section that the student got in grading system(C heading)). In the complete analysis use the word Overall Score only once because my logic to show meter fills look for the word "Overall Score" so just return this only once as the (sum of scores in all sections/100).  
-When you get the specific word Section wise analysis as well as the headings in it like Education add : for example Education: , Projects : , etc.  

1. Section by section - analysis starting from “A)” — make it visually clean and readable (line breaks between sections and also after section by section analysis add : and then start the content of it)  
2. An **Overall Score -** Add a full stop after the score.  
3. Section-wise Scores -(e.g., *Education: 8/10*, *Projects: 17/20*) — with full stops.  
4. **3–5 Personalized Suggestions** to improve the resume.  
5. Highlight any **critical errors** (missing contact info, broken links, improper formatting).  
6. Maintain a **constructive and supportive tone** like a mentor guiding a student.  
7. Be **strict but fair**. Only award marks when the resume *truly demonstrates* skills or achievements. Do NOT give full marks unless fully deserved.  
- After all scores either it is sectionwise analysis score or any score add full stop after that.

---

### EXAMPLES OF GOOD PRACTICES TO ENCOURAGE:
- “Built a full-stack MERN web app deployed on Vercel with 4K+ monthly users.”
- “Solved 700+ DSA problems, 5⭐ on CodeChef, Specialist on Codeforces.”
- “Contributed to open-source on GitHub: merged 3 PRs in JavaScript-based ML repo.”
- “Created a cloud-native CI/CD pipeline using GitHub Actions and Docker.”

Avoid polite inflation. Your job is to help students understand their real standing and improve.
- After all scores either it is sectionwise analysis score or any score add full stop after that.
"""
    response = model.generate_content([
        {"role": "user", "parts": [
            {"text": prompt},
            {"text": "Resume Content:"},
            {"text": resume_text}
        ]}
    ])

    return response.text