import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_FP_Placement(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Food Processing Engineering placements**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for Food Processing Placement)

✅ **Food Processing Placement Guidelines:**
- Prioritize key areas: **Food Technology, Unit Operations, Food Safety & Quality Control, Nutrition, Microbiology, Food Packaging, Food Plant Operations**
- Reward knowledge of relevant standards and tools: **HACCP, FSSAI, ISO 22000, GMP, GC-MS, HPLC, SPSS, MATLAB (for process modeling)**
- Appreciate domain-specific projects: **product shelf-life analysis, plant layout simulation, food preservation techniques, novel food product development**
- Reward internships at **food industries, R&D centers, quality control labs, food packaging units**
- Penalize software-only or unrelated projects with no relevance to food tech or processing

---

### C) GRADING SYSTEM (Total: 100 marks)

Each section contributes specific marks:

- **Education** (10 marks)  
  - +5 for CGPA/percentage  
  - +1 for school/college names  
  - +2 for years of 10th & 12th  
  - +2 if board names are given  
  - -2 for formatting or clarity issues  

- **Relevant Coursework** (10 marks)  
  - +8 for food-related courses (Food Chemistry, Safety, Tech, Microbiology)  
  - +2 for electives like Food Packaging or Nutrition  
  - -2 for irrelevant or missing courses  

- **Projects** (20 marks)  
  - +6 for product or plant-based food tech projects  
  - +5 for shelf life analysis, packaging studies, or QMS modeling  
  - +4 for simulation tools like MATLAB/SPSS  
  - -2 for no results, unclear data, or vague goal  
  - -1 for grammar issues  

- **Technical Skills** (20 marks)  
  - +5 for lab techniques: GC, HPLC, TSS, pH, texture  
  - +5 for quality systems: HACCP, FSSAI, ISO 22000  
  - +5 for tools: MATLAB, SPSS, MS Excel (stats), AutoCAD for layout  
  - Penalize irrelevant software or vague listings  

- **Work Experience / Internships** (10 marks)  
  - +10 for internships in core industries (processing, QMS, food safety)  
  - +5 for training in labs or small-scale food units  
  - -2 for non-core or generic roles  

- **Achievements & Certifications** (10 marks)  
  - +5 for certifications in HACCP, FSSAI, ISO, QA/QC, etc.  
  - +5 for paper presentations, food tech contests, product expos  
  - Score based on industry relevance  

- **Extra-curricular Activities** (10 marks)  
  - Reward events related to nutrition awareness, agri-food tech expos, college clubs  
  - Penalize irrelevant or filler content  

- **Contact Info + ATS Formatting** (5 marks)  
  - +5 for phone, email, LinkedIn, GitHub/portfolio all present  
  - -2 for one missing  
  - -3 for poor formatting (multi-column, tables)  

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward quantified data: shelf life in days, weight loss %, spoilage %  
  - Penalize grammar issues, lack of units/values

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
- “Analyzed microbial stability of packaged tomato puree over 30 days under refrigeration.”
- “Completed HACCP Level 2 Certification and implemented SOP for hygiene audit.”
- “Simulated thermal processing curve for milk pasteurization using MATLAB.”
- “Interned at Nestlé QA Lab; analyzed TSS, viscosity, and packaging strength of dairy products.”

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