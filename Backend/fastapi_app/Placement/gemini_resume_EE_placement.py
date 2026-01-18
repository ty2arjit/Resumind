import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_EE_Placement(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Electrical Engineering placements**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for Electrical Engineering Placement)

✅ **Electrical Placement Guidelines:**
- Prioritize core knowledge: **Power Systems, Control Systems, Power Electronics, Electrical Machines, Circuit Theory, Signal Processing**
- Reward knowledge of tools like **MATLAB/Simulink, PSCAD, ETAP, LabVIEW, AutoCAD Electrical, PSpice**
- Reward projects involving **power distribution, motor control, automation, circuit analysis, renewable energy systems**
- Prefer internships in **electrical utilities, core industries, switchgear companies, power plants, substations**
- Penalize vague projects or missing results like load, voltage, power factor, % efficiency
- Reward smart grid/IoT-energy integrations and embedded electrical systems

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
  - +8 for EE core subjects  
  - +2 for smart grid, PLC, IoT integration courses  
  - -2 for unstructured or off-topic listings  

- **Projects** (20 marks)  
  - +6 for simulations or hardware-based EE projects  
  - +5 for solar, automation, energy audit projects with numbers  
  - +3 for control system or embedded projects  
  - -2 for lack of measurements or vague objective  
  - -1 for poor grammar  

- **Technical Skills** (20 marks)  
  - Reward EE-specific software/tools & controller knowledge  
  - Grouping preferred: Simulation, Measurement, CAD, Programming  
  - Penalize irrelevant or overly generic tech lists  

- **Work Experience / Internships** (10 marks)  
  - +10 for experience in power plants, electrical utilities, or switchgear  
  - +5 for short-term or training-based internships  
  - -2 for unclear work or non-core roles  

- **Achievements & Certifications** (10 marks)  
  - +5 for certifications in PLC/SCADA, MATLAB, automation  
  - +5 for paper presentations, GATE qualification, tech events  
  - Score based on relevance and credibility  

- **Extra-curricular Activities** (10 marks)  
  - Reward leadership, tech clubs (IEEE), volunteering with technical events  
  - Penalize content with no measurable impact  

- **Contact Info + ATS Formatting** (5 marks)  
  - +5 for phone, email, LinkedIn, GitHub all present  
  - -2 for one missing  
  - -3 for improper formatting (tables, columns)  

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward clarity, action verbs, numbers (e.g. 220V, 1.5kW, 93% efficiency)  
  - Penalize passive tone, grammar issues, poor formatting

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
- “Designed and simulated 3-phase induction motor control system using MATLAB Simulink.”
- “Completed internship at NTPC, studied turbine-generator synchronization and fault protection circuits.”
- “Implemented smart solar inverter system using MPPT and Arduino.”
- “Performed energy audit of academic building, suggested 12% reduction in annual consumption.”

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