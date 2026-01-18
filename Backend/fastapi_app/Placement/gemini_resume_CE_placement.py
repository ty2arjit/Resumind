import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_CE_Placement(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Civil Engineering placements**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for Civil Engineering Placement)

✅ **Civil Placement Guidelines:**
- Emphasize core subjects: **Structural Engineering, RCC, Steel Design, Transportation, Geotechnical Engineering, Hydraulics, Surveying**
- Reward experience with tools like **AutoCAD, STAAD Pro, ETABS, Revit, SAP2000, Primavera, MS Project**
- Reward internships with **construction firms, site experience, surveying projects**
- Appreciate knowledge of **building codes, safety standards, sustainability**
- Encourage quantifiable project outcomes — cost, load, area, etc.
- Penalize vague bullet points or unrelated software/tools
- Do not reward general coding projects unless linked to civil applications

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
  - +8 for CE core courses  
  - +2 for construction management, sustainable design, GIS  
  - -2 for poor formatting/lack of clarity  

- **Projects** (20 marks)  
  - +6 per practical/realistic project (e.g., design of G+3 RCC building, bridge simulation)  
  - +4 for simulation, load analysis, or construction management models  
  - +2 for college-level design projects  
  - -2 if vague scope or missing results  
  - -1 for each grammar/spelling issue  

- **Technical Skills** (20 marks)  
  - Reward knowledge of design, drafting, structural analysis software  
  - Prefer skills grouped into: Design Tools, Analysis Tools, Management Tools  
  - Penalize bloated or irrelevant software mentions  

- **Work Experience / Internships** (10 marks)  
  - +10 for relevant field experience with measurable outcomes  
  - +5 for academic training or summer work  
  - -2 for vague or unrelated content  

- **Achievements & Certifications** (10 marks)  
  - +5 for certifications in structural design, green building, construction safety  
  - +5 for paper presentations, modeling competitions, field workshop  
  - Score based on credibility and alignment  

- **Extra-curricular Activities** (10 marks)  
  - Reward involvement in NSS/NCC, environment drives, team projects, leadership  
  - Penalize if unimpactful or off-topic  

- **Contact Info + ATS Formatting** (5 marks)  
  - +5 if phone, email, LinkedIn, GitHub/portfolio all present  
  - -2 for missing one  
  - -3 for ATS-incompatible formatting  

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward concise writing with numbers and outcomes  
  - Penalize grammatical or style errors

---

### D) #FINAL OUTPUT

#At the end of your analysis, **return the following**:

-Don't use integers to start a line/heading or use without full stop because the line breaks after full stop in our UI so I don't want a full stop in between the heading and starting number.  
-Overall Score = XX/100. (XX is the sum of scores in each section that the student got in grading system(C heading))  
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
- “Designed a two-storey RCC building using STAAD Pro with load combination and deflection analysis.”
- “Interned at L&T Construction, assisted in project scheduling and site supervision.”
- “Completed certification in Primavera and applied CPM techniques on sample project.”
- “Modeled water distribution system using EPANET and optimized pressure zones.”

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
