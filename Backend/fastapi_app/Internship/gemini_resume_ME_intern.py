import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_ME_Intern(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Mechanical Engineering internships**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for Mechanical Engineering Intern)

✅ **Mechanical Engineering Internship Guidelines:**
- Prioritize subjects like **Thermodynamics, Fluid Mechanics, Strength of Materials, CAD, Heat Transfer, Manufacturing Processes, Mechanics, Machine Design**
- Reward practical work involving **CAD/CAE tools (SolidWorks, AutoCAD, ANSYS, Creo)**, **MATLAB**, **3D printing**, **CAM tools**
- Reward hands-on exposure in **automotive, manufacturing, thermal**, or **mechanical design** domains
- Reward technical competitions (e.g. SAE BAJA, Go-Kart, ASME events), plant training, and research projects
- Penalize generic projects or unclear roles in team projects
- Do not penalize for lack of full-time experience (internship profile)

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
  - +8 for core mechanical subjects  
  - +2 for interdisciplinary (e.g., mechatronics, design optimization)  
  - -2 for formatting/lack of clarity  

- **Projects** (20 marks)  
  - +5 for each technical/mechanical project  
  - +5 for simulation/design-based work with tools  
  - +3 for innovative or optimized mechanical systems  
  - -2 for vague outcomes or no contribution mentioned  
  - -1 per grammar/spelling error  

- **Technical Skills** (20 marks)  
  - Reward CAD/CAE/CFD tools, machining tools, and software like **SolidWorks, ANSYS, MATLAB, Fusion 360**  
  - Penalize cluttered or irrelevant skills  
  - Reward categorized structure (e.g., Design, Simulation, Programming)

- **Achievements & Certifications** (15 marks)  
  - +10 for technical events, competitions, internships in core ME  
  - +5 for certifications (NPTEL, Coursera in CFD, Design, or Thermo)  
  - Score based on relevance and impact  

- **Extra-curricular Activities** (10 marks)  
  - Reward clubs, fests, leadership in SAE, ASME, or innovation cells  
  - Penalize vague, unrelated content  

- **Contact Info + ATS Formatting** (10 marks)  
  - +10 if phone, email, LinkedIn, GitHub/portfolio all present  
  - -2 for missing one  
  - -5 for missing two or more  
  - -3 for poor ATS formatting (multi-column, tables, images)  

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward clarity, technical accuracy, and metric-backed outcomes  
  - Penalize grammar or awkward phrasing

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
- “Simulated stress analysis on a bike chassis using ANSYS and improved weight-to-strength ratio by 12%.”
- “Designed and fabricated a pneumatic pick-and-place system using SolidWorks and 3D-printed joints.”
- “Completed plant training at BHEL on turbine assembly and thermal energy flow.”
- “Programmed automated material cutting process using CAM tools, reducing waste by 20%.”

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