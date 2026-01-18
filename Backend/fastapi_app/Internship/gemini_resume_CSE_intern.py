import os
import google.generativeai as genai;
from dotenv import load_dotenv;

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_CSE_Intern(resume_text,position_type,field):
  prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Computer Science/Software Engineering internships**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for CSE Intern)

✅ **CSE Internship Guidelines:**
- Prioritize core skills: **Data Structures, Algorithms, OOP, DBMS, OS, CN**
- Reward **competitive programming achievements**: Codeforces/LeetCode/CodeChef
- Reward **GitHub/LinkedIn/portfolio links**, especially with live project demos
- Reward meaningful **internships, hackathons, open source contributions**
- Look for **project variety and clarity**, especially use of tech stack
- Penalize projects without links or poor/no descriptions
- Do not penalize absence of job experience (internship role)

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
  - +9 if DSA, OOP, DBMS are present (even in synonyms)
  - +1 for any other CSE-relevant subject
  - -2 for formatting/lack of clarity

- **Projects** (20 marks)
  - +5 for each well-described project (minimum 2)
  - +2–3 for minor/simple projects
  - +5 if full-stack/advanced tech used
  - -2 for missing links, vague scope, no outcome
  - -1 per grammatical issue

- **Technical Skills** (20 marks)
  - Score based on relevance, depth, and variety
  - Penalize for keyword stuffing or unsubstantiated tools
  - Reward clear categorization (e.g. Languages, Frameworks)

- **Achievements & Certifications** (15 marks)
  - +10 for strong CP profiles (e.g. Pupil/Expert on CF)
  - +5 for Hackathons, GSoC, ML contests, certifications
  - Score based on field relevance

- **Extra-curricular Activities** (10 marks)
  - Judge soft skills, leadership, impact
  - Reward quantified impact or real metrics
  - Penalize vague/filler content

- **Contact Info + ATS Formatting** (10 marks)
  - +10 if phone, email, LinkedIn, GitHub all present
  - -2 for missing one
  - -5 for missing two or more
  - -3 for poor ATS formatting (multi-column, tables, images)

- **Writing, Grammar, Metrics** (5 marks)
  - Reward action verbs, grammar, quantified achievements
  - Penalize spelling mistakes or missing numbers in bullet points

---

### D) #FINAL OUTPUT

#At the end of your analysis, **return the following**:

-Don't use integers to start a line/ heading or use without full stop because the line breaks after full stop in our UI so i don't want a full stop in between the heading and starting number.
-Overall Score = XX/100. (XX is the sum of scores in each section that the student got in grading system(C heading)).In the complete analysis use the word Overall Score only once because my logic to show meter fills look for the word "Overall Score" so just return this only once as the (sum of scores in all sections/100).
-When you get the specific word Section wise analysis as well as the headings in it like Education add : for example Education: , Projects : , etc.
1. Section by section - analysis starting from “A)” — make it visually clean and readable (line breaks between sections and also after section by section analysis add : and then start the content of it)
2. An **Overall Score -** Add a full stop after the score.
3. Section-wise Scores -(e.g., *Education: 8/10*, *Projects: 17/20*) — with full stops.
4. **3–5 Personalized Suggestions** to improve the resume.
5. Highlight any **critical errors** (missing contact info, broken links, improper formatting).
6. Maintain a **constructive and supportive tone** like a mentor guiding a student.
7. Be **strict but fair**. Only award marks when the resume *truly demonstrates* skills or achievements. Do NOT give full marks unless fully deserved.

When integers are used to start a line or point avoid using full stop after that use closed parenthesis.
---

### EXAMPLES OF GOOD PRACTICES TO ENCOURAGE:
- “Reduced build time by 35% using Webpack optimization.”
- “Solved 400+ LeetCode problems with a rating of 1850+.”
- “Created full-stack MERN app deployed on Vercel with 1k+ users.”
- “Led a 5-member team in GDSC for organizing HackathonX.”

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