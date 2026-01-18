import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def resume_analysis_Analytics_Placement(resume_text, position_type, field):
  prompt = f""" 
You are an expert AI Resume Evaluator for an application called **Resumind**. Your task is to evaluate a resume for a **{position_type}** role in the **{field}** domain — with a specific focus on **Analytics placements**. You must assess the resume using strict and realistic **ATS-style criteria**, ensuring fairness, accuracy, and precision. Avoid inflating scores or giving marks without evidence.

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

### B) FIELD-SPECIFIC & POSITION-TYPE INSTRUCTIONS (for Analytics Placement)

✅ **Analytics Placement Guidelines:**
- Prioritize **real-world experience** in analytics, insights generation, and data storytelling  
- Reward use of **Python (pandas, numpy, scikit-learn), SQL (joins, CTEs), Excel, Power BI, Tableau**  
- Reward **internships** or work that shows business impact through data  
- Projects must show clear outcomes, metrics (e.g., “reduced churn by 8%”), and structured workflow  
- Value use of **A/B testing, regression, clustering, dashboards, and automation**  
- Penalize unclear problem statements, missing KPIs, or over-general claims

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
  - +5 for core subjects: Data Analytics, Statistics, Business Intelligence  
  - +3 for electives: Machine Learning, Forecasting, Econometrics  
  - +2 for coursework with clear impact relevance  
  - -2 for unrelated or vague listings  

- **Projects** (20 marks)  
  - +10 for impactful analytics projects with metrics and clear outcomes  
  - +5 for modeling, clustering, or A/B testing  
  - +3 for dashboards/EDA on public data  
  - -2 for missing links, unclear scope, lack of impact  
  - -1 per grammatical issue  

- **Technical Skills** (20 marks)  
  - Score based on relevance, clarity, and substantiation  
  - Reward proficiency in Python, SQL, Power BI/Tableau, Excel  
  - Penalize jargon without examples  
  - Reward clear tool categorization (e.g., Languages, Visualization Tools)  

- **Work Experience / Internships** (10 marks)  
  - +10 for analytics internships or placements with measurable results  
  - +5 for freelance/part-time roles in analytics/reporting  
  - -2 for vague, unsupported job claims  

- **Achievements & Certifications** (10 marks)  
  - +5 for relevant certifications (Google, Coursera, Microsoft)  
  - +5 for winning/participating in analytics competitions, Kaggle rank, papers  
  - Score based on relevance and evidence  

- **Extra-curricular Activities** (10 marks)  
  - Reward analytical roles in clubs/events (e.g., data contests, biz analytics cells)  
  - Penalize unrelated or filler content  

- **Contact Info + ATS Formatting** (5 marks)  
  - +5 if phone, email, LinkedIn, GitHub/portfolio all present  
  - -2 for missing one  
  - -3 for ATS-unfriendly formatting (tables, columns, graphics)  

- **Writing, Grammar, Metrics** (5 marks)  
  - Reward action verbs, quantified achievements  
  - Penalize spelling errors or vague bullet points  

---

### D) #FINAL OUTPUT

#At the end of your analysis, **return the following**:

-Don't use integers to start a line/ heading or use without full stop because the line breaks after full stop in our UI so I don't want a full stop in between the heading and starting number.  
-Overall Score = XX/100. (XX is the sum of scores in each section that the student got in grading system(C heading)). In the complete analysis use the word Overall Score only once because my logic to show meter fills look for the word "Overall Score" so just return this only once as the (sum of scores in all sections/100).  
-When you get the specific word Section wise analysis as well as the headings in it like Education add : for example Education: , Projects : , etc.  

1. Section by section - analysis starting from “A)” — make it visually clean and readable (line breaks between sections and also after section by section analysis add : and then start the content of it)  
2. An **Overall Score -** Add a full stop after the score.  
3. Section-wise Scores -(e.g., *Education: 8/10*, *Projects: 17/20*) — with full stops.  
4. **3–5 Personalized Suggestions** to improve the resume.  
5. Highlight any **critical errors** (missing contact info, broken links, improper formatting).  
6. Maintain a **constructive and supportive tone** like a mentor guiding a student.  
7. Be **strict but fair**. Only award marks when the resume *truly demonstrates* skills or achievements. Do NOT give full marks unless fully deserved.

When integers are used to start a line or point avoid using full stop after that use closed parenthesis.

---

### EXAMPLES OF GOOD PRACTICES TO ENCOURAGE:
- “Led analytics project to reduce delivery time by 15% using geospatial clustering.”  
- “Built Power BI dashboard for sales KPIs across 4 regions with real-time filters.”  
- “Automated weekly reporting with Python and SQL, saving 6+ hours/week.”  
- “Performed logistic regression to predict customer churn with 80%+ accuracy.”

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