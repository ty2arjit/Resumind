import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_ECE_Intern(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Electronics and Communication Engineering internships**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for ECE Intern)

✅ **ECE Internship Guidelines:**
- Prioritize subjects like **Digital Electronics, Analog Circuits, Signals & Systems, Communication Systems, VLSI, Microprocessors, Embedded Systems**
- Reward hands-on experience with **Arduino, Raspberry Pi, PCB design, MATLAB, Verilog/VHDL**
- Reward knowledge of **communication protocols (UART, I2C, SPI)** and simulation tools like **Multisim, Proteus, Xilinx**
- Software skills like **MATLAB, Python, C/C++** are a plus if applied in hardware-oriented projects
- Reward internships, electronics-based hackathons, or hardware/IoT-based projects
- Penalize vague or overly software-oriented projects with no relevance to ECE core
- Do not penalize for lack of job experience (internship role)

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
  - +8 for ECE subjects listed  
  - +2 for electives like IoT, AI, Robotics (if applied in hardware context)  
  - -2 for formatting/lack of clarity  

- **Projects** (20 marks)  
  - +5 for each ECE/hardware-based project with good description  
  - +5 if embedded systems/PCB design/IoT used  
  - +3 for software-controlled hardware  
  - -2 for unclear objectives, no results  
  - -1 per grammar/spelling issue  

- **Technical Skills** (20 marks)  
  - Reward tools like **MATLAB, Verilog, Proteus, Arduino IDE, Xilinx, Keil**  
  - Organize into categories (Hardware Tools, Programming, Simulation)  
  - Penalize skill stuffing or irrelevant tech  

- **Achievements & Certifications** (15 marks)  
  - +10 for hardware hackathons, certifications (IoT, VLSI), research papers  
  - +5 for Coursera/NPTEL or electronics-related trainings  
  - Score based on ECE relevance  

- **Extra-curricular Activities** (10 marks)  
  - Reward technical clubs (robotics, IoT), project expos, or volunteering  
  - Penalize generic or unstructured points  

- **Contact Info + ATS Formatting** (10 marks)  
  - +10 if phone, email, LinkedIn, GitHub/portfolio all present  
  - -2 for missing one  
  - -5 for missing two or more  
  - -3 for poor ATS formatting (multi-column, tables, images)  

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward structured language, engineering terminology, numbers  
  - Penalize errors, filler content

---

### D) #FINAL OUTPUT

#At the end of your analysis, **return the following**:

-Don't use integers to start a line/heading or use without full stop because the line breaks after full stop in our UI so I don't want a full stop in between the heading and starting number.  
-Overall Score = XX/100. (XX is the sum of scores in each section that the student got in grading system(C heading)).In the complete analysis use the word Overall Score only once because my logic to show meter fills look for the word "Overall Score" so just return this only once as the (sum of scores in all sections/100).
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
- “Designed and fabricated a PCB for IoT-based smart irrigation system.”
- “Simulated QPSK modulation using MATLAB and analyzed BER curve.”
- “Developed a home automation project using ESP32 and Blynk platform.”
- “Built traffic signal controller using Verilog and simulated in Xilinx Vivado.”

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