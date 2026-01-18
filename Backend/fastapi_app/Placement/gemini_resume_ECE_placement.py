import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_ECE_Placement(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Electronics and Communication Engineering placements**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for ECE Placement)

✅ **ECE Placement Guidelines:**
- Prioritize ECE core: **Digital Electronics, Analog Circuits, Communication Systems, VLSI, Signal Processing, Microprocessors, Embedded Systems**
- Reward experience with tools: **MATLAB, Verilog, VHDL, Multisim, Cadence, Xilinx, KiCAD, Arduino, Raspberry Pi**
- Appreciate internships or research in **hardware design, telecommunications, IoT, signal processing, embedded programming**
- Emphasize practical application: **simulation results, hardware testing, circuit designs**
- Reward CP achievements if targeting software-focused roles (optional)
- Penalize generic or unrelated projects with no ECE relevance

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
  - +8 for ECE core courses  
  - +2 for electives (AI in Electronics, IoT, Wireless Communication)  
  - -2 for missing subjects or poor formatting  

- **Projects** (20 marks)  
  - +6 for circuit-based or embedded projects with proper explanation  
  - +5 for IoT/communication system design  
  - +3 for software/signal modeling (MATLAB, Simulink)  
  - -2 for vague scope or no hardware/simulation detail  
  - -1 for grammar issues  

- **Technical Skills** (20 marks)  
  - Reward categorized tools: Circuit Design, Simulation, Microcontrollers  
  - Penalize bloated or irrelevant software  
  - +2–3 for structured skill listing  

- **Work Experience / Internships** (10 marks)  
  - +10 for telecom/embedded/VLSI internships  
  - +5 for research assistantship or hardware-based college training  
  - -2 for unclear roles or results  

- **Achievements & Certifications** (10 marks)  
  - +5 for IEEE paper presentations, tech events, circuit design contests  
  - +5 for certifications in embedded systems, IoT, or EDA tools  
  - Score based on relevance  

- **Extra-curricular Activities** (10 marks)  
  - Reward team events, student chapter work (e.g. IEEE), leadership  
  - Penalize off-topic or non-impactful bullets  

- **Contact Info + ATS Formatting** (5 marks)  
  - +5 for all info (email, phone, LinkedIn, GitHub)  
  - -2 for missing one  
  - -3 for tables or multi-column layout  

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward quantified results: efficiency %, power savings, Hz, volts  
  - Penalize errors or passive, unstructured writing

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
- “Designed and simulated FIR filter using MATLAB and verified using FFT plot.”
- “Built a line-following robot using IR sensors and Arduino; improved navigation accuracy by 20%.”
- “Completed 2-month internship at BSNL, observed modulation schemes and transmission setup.”
- “Developed Verilog code for ALU and tested using ModelSim.”

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