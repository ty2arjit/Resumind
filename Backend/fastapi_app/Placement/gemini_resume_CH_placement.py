import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_CH_Placement(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Chemical Engineering placements**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for Chemical Engineering Placement)

✅ **Chemical Placement Guidelines:**
- Prioritize subjects like **Process Calculations, Thermodynamics, Reaction Engineering, Fluid Mechanics, Heat & Mass Transfer, Process Control**
- Reward experience in using **Aspen Plus, DWSIM, MATLAB, ChemCAD, AutoCAD P&ID**, Excel modeling, etc.
- Reward plant visits, industrial internships (chemical plants, refineries, pharma, food), process simulation projects
- Appreciate projects involving **material balance, energy optimization, catalyst design, distillation, scale-up**
- Reward awareness of **HSE standards**, **PFD/P&ID design**, and **unit operations**
- Penalize vague project descriptions or missing output/metrics
- Avoid giving credit for generic CS/IT skills unless applied to chemical simulations or process modeling

---

### C) GRADING SYSTEM (Total: 100 marks)

Each section contributes specific marks:

- **Education** (10 marks)  
  - +5 for CGPA/percentage  
  - +1 for school/college names  
  - +2 for years of 10th & 12th  
  - +2 if board names are given  
  - -2 for formatting or unclear details  

- **Relevant Coursework** (10 marks)  
  - +8 for CH core courses  
  - +2 for electives like Industrial Safety, Data Analytics for Process Control, etc.  
  - -2 for clutter or missing context  

- **Projects** (20 marks)  
  - +6 for detailed process modeling/optimization project  
  - +5 for industrial relevance and outcomes (yields, energy savings)  
  - +3 for software use (Aspen, ChemCAD)  
  - -2 for lack of impact/results  
  - -1 per grammar or formatting issue  

- **Technical Skills** (20 marks)  
  - Reward simulation tools, PFD/P&ID tools, lab instruments  
  - Prefer grouping: Simulation Tools, Lab Techniques, Analysis  
  - Penalize bloated or irrelevant lists  

- **Work Experience / Internships** (10 marks)  
  - +10 for chemical plant, refinery, R&D internship  
  - +5 for minor or short-term role  
  - -2 for vague responsibilities or lack of quantifiable output  

- **Achievements & Certifications** (10 marks)  
  - +5 for certified training (e.g., Process Safety, MATLAB, DWSIM, Aspen)  
  - +5 for competitions, papers, simulations, or chemical case studies  

- **Extra-curricular Activities** (10 marks)  
  - Reward professional society work (e.g., IIChE), leadership roles, event management  
  - Penalize unrelated or filler content  

- **Contact Info + ATS Formatting** (5 marks)  
  - +5 for complete contact info (phone, email, LinkedIn, GitHub)  
  - -2 for one missing  
  - -3 for bad formatting (multi-column, tables)

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward clean language, use of units (kg/hr, °C, %, etc.)  
  - Penalize spelling/grammar issues and wordy writing

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
- “Simulated distillation column in Aspen Plus to recover 92% ethanol with reduced energy usage.”
- “Completed 2-month internship at Indian Oil; performed pressure drop calculations and assisted in flare stack inspection.”
- “Designed and validated P&ID for batch reactor system using AutoCAD and DWSIM.”
- “Worked on catalyst regeneration in fixed-bed reactor for hydrogen production.”

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