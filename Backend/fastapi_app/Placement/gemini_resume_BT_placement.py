import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_BT_Placement(resume_text, position_type, field):
    prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Biotechnology placements**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for Biotechnology Placement)

✅ **Biotech Placement Guidelines:**
- Prioritize subjects like **Genetic Engineering, Molecular Biology, Bioprocess Engineering, Immunology, Microbiology, Bioinformatics**
- Reward hands-on work in **PCR, DNA extraction, SDS-PAGE, ELISA, Fermentation, Cell Culture, CRISPR**, etc.
- Reward use of biotech tools: **BLAST, ClustalW, PyMOL, R, Bioconductor, Python (for bio data), Excel for analytics**
- Reward internships in **labs, pharma/biotech companies, R&D**, or healthcare startups
- Encourage awareness of **GMP, GLP, regulatory practices**, and lab safety protocols
- Penalize vague bullet points, over-generalized skills, poor formatting
- Do not reward non-biotech projects unless clearly interdisciplinary

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
  - +8 for core biotech subjects  
  - +2 for electives like Computational Biology, Biostatistics, Omics Technologies  
  - -2 for formatting/lack of clarity  

- **Projects** (20 marks)  
  - +6 for core biotech research projects or industrial applications  
  - +5 for lab-based/experimental validation (wet-lab)  
  - +3 for modeling/simulation/bioinformatics pipelines  
  - -2 for unclear goals/results  
  - -1 per spelling/grammar issue  

- **Technical Skills** (20 marks)  
  - Reward tools like PCR, MATLAB (bio), R, Bioconductor, Geneious, MS Excel  
  - Penalize unrelated or bloated lists  
  - Encourage grouping into: Wet Lab, Computational, Analytical

- **Work Experience / Internships** (10 marks)  
  - +10 for biotech company or lab internship with defined outcomes  
  - +5 for short-term or academic-based internships  
  - -2 if the experience is too vague or general  

- **Achievements & Certifications** (10 marks)  
  - +5 for certifications in biotech-specific platforms (Coursera, NPTEL, etc.)  
  - +5 for research papers, presentations, competitions, IP filings  
  - Score based on depth and field alignment  

- **Extra-curricular Activities** (10 marks)  
  - Reward technical volunteering, biotech clubs, NGOs, bio events  
  - Penalize generic entries with no impact  

- **Contact Info + ATS Formatting** (5 marks)  
  - +5 if phone, email, LinkedIn, GitHub all present  
  - -2 for missing one  
  - -3 for poor ATS formatting (tables, multi-column layouts)

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward quantifiable impact and good grammar  
  - Penalize spelling mistakes or ambiguous terms

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
- “Analyzed gene expression data using R and visualized differential expression with heatmaps.”
- “Completed 2-month internship at Biocon; assisted in protein purification using chromatography.”
- “Designed CRISPR guide RNA sequences for gene editing of E. coli strain.”
- “Presented poster at BioAsia 2024 on molecular docking of anticancer compounds.”

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