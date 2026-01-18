import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_CR_Placement(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Ceramic Engineering placements**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for Ceramic Engineering Placement)

✅ **Ceramic Placement Guidelines:**
- Prioritize core areas: **Ceramic Processing, Glass Technology, Refractory Materials, Powder Metallurgy, Characterization Techniques, Phase Diagrams**
- Reward knowledge of **thermal analysis, sintering, solid-state reactions, SEM, XRD, TGA, DTA, FESEM, EDS**
- Reward internships and projects in **tile, glass, refractories, advanced ceramics, defense, or aerospace**
- Appreciate use of tools like **MATLAB (for materials modeling), Origin, ThermoCalc, Minitab, ImageJ, AutoCAD**
- Reward quantitative project data like **composition %, sintering temperature, shrinkage %, porosity, thermal conductivity**
- Penalize vague, general, or non-engineering content
- Avoid awarding marks for non-ceramic projects unless interdisciplinary relevance is clearly explained

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
  - +8 for ceramic/materials subjects  
  - +2 for electives like nanotechnology, thermodynamics, material mechanics  
  - -2 for vague/unorganized list  

- **Projects** (20 marks)  
  - +6 for ceramic-focused research, product design or testing  
  - +5 for industry project with quantifiable results (density, porosity, thermal resistance)  
  - +3 for modeling/simulation  
  - -2 for lack of conclusions  
  - -1 for language errors  

- **Technical Skills** (20 marks)  
  - Reward tools for thermal, microstructure, and material analysis  
  - Prefer grouping: Characterization Tools, Software, Lab Instruments  
  - Penalize bloated or irrelevant skills  

- **Work Experience / Internships** (10 marks)  
  - +10 for core internships in ceramic/glass/refractory companies  
  - +5 for research assistantships or relevant summer training  
  - -2 if unclear role or outputs  

- **Achievements & Certifications** (10 marks)  
  - +5 for workshops/courses on XRD, DTA, SEM, ceramic processing  
  - +5 for publications, poster presentations, competitions, certifications  
  - -2 if vague or not related to core field  

- **Extra-curricular Activities** (10 marks)  
  - Reward leadership roles, technical society work (IIM, ACerS)  
  - Penalize filler content with no impact  

- **Contact Info + ATS Formatting** (5 marks)  
  - +5 for phone, email, LinkedIn, GitHub/portfolio all present  
  - -2 for one missing  
  - -3 for poor formatting or use of tables  

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward precision, units, composition values  
  - Penalize grammar/spelling issues or unstructured bullets

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
- “Prepared alumina-zirconia composite via slip casting; achieved 98.6% density after sintering at 1550°C.”
- “Completed internship at Saint-Gobain India: assisted in thermal shock testing and microstructure evaluation.”
- “Used XRD and SEM to analyze phase purity and grain structure of synthesized BaTiO3.”
- “Performed thermal conductivity measurement and shrinkage analysis using DTA and Archimedes method.”

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