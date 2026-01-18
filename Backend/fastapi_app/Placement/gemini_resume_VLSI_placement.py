import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_VLSI_Placement(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **VLSI (Very Large Scale Integration) placements**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for VLSI Placement)

✅ **VLSI Placement Guidelines:**
- Emphasize core concepts: **Digital Design, CMOS, ASIC, FPGA, SoC, Timing Analysis, RTL Design, Physical Design**
- Strongly reward proficiency in **Verilog, VHDL, SystemVerilog**, as well as knowledge of **UVM**, **DFT**, and **synthesis/STA concepts**
- Reward hands-on experience with **EDA tools**: **Cadence, Synopsys, Mentor Graphics, Vivado, ModelSim, Quartus, SpyGlass**
- Prefer **projects** on **RTL design, verification, DFT insertion, synthesis**, or any FPGA/ASIC flow
- Internships in **semiconductor companies, fab units, or hardware IP firms** are highly valuable
- Penalize vague projects, poor tool usage, or lack of RTL/verification depth

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
  - +8 for core subjects (Digital Electronics, Microelectronics, VLSI Design, HDL)  
  - +2 for electives like Embedded Systems, SoC, CMOS Fabrication  
  - -2 for irrelevant or unclear listings  

- **Projects** (20 marks)  
  - +10 for RTL/Verification/Physical Design projects with tool usage  
  - +5 for synthesis, DFT, FPGA implementation  
  - +5 for clear results (timing, area, power, performance)  
  - -2 for lack of outcome or unclear flow  
  - -1 for grammar mistakes  

- **Technical Skills** (20 marks)  
  - +10 for HDL (Verilog, VHDL, SystemVerilog), UVM  
  - +5 for EDA tools (Synopsys, Cadence, Mentor, Vivado)  
  - +5 for scripting languages (Python, TCL, Shell)  
  - Penalize buzzwords with no evidence  

- **Work Experience / Internships** (10 marks)  
  - +10 for internships in semiconductor/VLSI domains  
  - +5 for training at IP companies or chip design roles  
  - -2 for unrelated experience  

- **Achievements & Certifications** (10 marks)  
  - +5 for certification in RTL/Verification/PD (e.g., from Udemy, VLSI Academy, NPTEL)  
  - +5 for research papers, project presentations, VLSI events  
  - Score based on depth and relevance  

- **Extra-curricular Activities** (10 marks)  
  - Reward contributions to tech clubs (e.g., IEEE, chip design groups)  
  - Penalize filler or non-technical fluff  

- **Contact Info + ATS Formatting** (5 marks)  
  - +5 for phone, email, LinkedIn, GitHub/portfolio all present  
  - -2 for one missing  
  - -3 for bad formatting (tables, columns, images)  

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward concise, metric-driven points (e.g., “Reduced area by 17% using logic optimization.”)  
  - Penalize spelling or grammar errors

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
- “Designed 4-bit ALU in Verilog, synthesized using Synopsys Design Compiler with 10% area reduction.”
- “Implemented UART receiver in FPGA using Vivado; verified using ModelSim with 100% functional coverage.”
- “Certified in Physical Design using Cadence Innovus by VLSI Academy.”
- “Presented paper on RISC-V SoC architecture at IEEE-VLSID 2024.”

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