import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_ID_Placement(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Industrial Design placements**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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
- Projects / Portfolio  
- Technical & Design Skills  
- Work Experience (if any)  
- Certifications / Achievements  
- Extra-curricular Activities  
- Formatting & ATS Compatibility  
- Give overall score as the sum of marks obtained in each section.

---

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for Industrial Design Placement)

✅ **Industrial Design Placement Guidelines:**
- Prioritize areas like **Product Design, Human-Centered Design, Ergonomics, Sustainable Design, CAD Modeling, Rapid Prototyping**
- Reward strong **portfolio links** with visuals, case studies, and descriptions of design process (research, ideation, prototyping, testing)
- Value practical knowledge of tools: **SolidWorks, Rhino, KeyShot, Adobe Suite, Figma, Blender, Fusion 360**
- Reward internships or design competitions with user-focused or impactful outcomes
- Penalize resumes lacking portfolio links or with vague project descriptions

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
  - +6 for ID-specific courses (Design Thinking, Aesthetics, Ergonomics)  
  - +4 for electives like UI/UX, Packaging Design, Materials in Design  
  - -2 for missing or unclear listings  

- **Projects / Portfolio** (20 marks)  
  - +10 for well-documented portfolio (with link, visuals, user journey, testing)  
  - +5 for impactful or innovative projects  
  - +5 for working prototypes, CAD renders, or usability testing  
  - -3 for no portfolio link  
  - -2 for vague problem or lack of research phase  

- **Technical & Design Skills** (20 marks)  
  - +5 for CAD tools (Fusion, SolidWorks, Rhino)  
  - +5 for Visualization & Rendering (KeyShot, Blender)  
  - +5 for UX/UI tools (Figma, Adobe XD, Illustrator)  
  - +5 for Sketching, Prototyping, Digital Fabrication (3D Printing, Laser Cutting)  
  - Penalize irrelevant tech or vague listings  

- **Work Experience / Internships** (10 marks)  
  - +10 for internships in design studios, product teams, or innovation labs  
  - +5 for freelance or small-scale client work  
  - -2 for unclear roles or non-design jobs  

- **Achievements & Certifications** (10 marks)  
  - +5 for design awards, competitions (e.g. iF, Red Dot, Toycathon, SIIC, etc.)  
  - +5 for certified courses in UI/UX, 3D modeling, prototyping, etc.  
  - Score based on relevance  

- **Extra-curricular Activities** (10 marks)  
  - Reward creative showcases (e.g., design fests, community design work, exhibitions)  
  - Penalize filler or unrelated content  

- **Contact Info + ATS Formatting** (5 marks)  
  - +5 for phone, email, LinkedIn, Behance/Portfolio/GitHub  
  - -2 for missing one  
  - -3 for multi-column, image-heavy formats  

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward clarity in design storytelling (challenge–approach–impact)  
  - Penalize spelling/grammar errors, vague statements

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
- “Redesigned kitchen tool with improved ergonomics; reduced hand strain by 30% (tested via user survey).”
- “Created fully 3D printed enclosure for wearable device; improved aesthetics and usability.”
- “Built Figma-based dashboard to monitor student wellness as part of design challenge.”
- “Portfolio link: www.behance.net/johndesigner (contains detailed case studies).”

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