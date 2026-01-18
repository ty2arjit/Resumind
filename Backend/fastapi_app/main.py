from fastapi import FastAPI, Request, UploadFile, File, Form
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
#from gemini_service import generate_resume_analysis
from utils.pdf_parser import extract_text_from_pdf
from Internship.gemini_resume_CSE_intern import resume_analysis_CSE_Intern
from Internship.gemini_resume_BM_intern import resume_analysis_BM_Intern
from Internship.gemini_resume_BT_intern import resume_analysis_BT_Intern
from Internship.gemini_resume_CE_intern import resume_analysis_CE_Intern
from Internship.gemini_resume_CH_intern import resume_analysis_CH_Intern
from Internship.gemini_resume_CR_intern import resume_analysis_CR_Intern
from Internship.gemini_resume_ECE_intern import resume_analysis_ECE_Intern
from Internship.gemini_resume_EE_intern import resume_analysis_EE_Intern
from Internship.gemini_resume_EI_intern import resume_analysis_EI_Intern
from Internship.gemini_resume_FP_intern import resume_analysis_FP_Intern
from Internship.gemini_resume_ID_intern import resume_analysis_ID_Intern
from Internship.gemini_resume_ME_intern import resume_analysis_ME_Intern
from Internship.gemini_resume_MN_intern import resume_analysis_MN_Intern
from Internship.gemini_resume_MT_intern import resume_analysis_MT_Intern
from Internship.gemini_resume_Analytics_intern import resume_analysis_Analytics_Intern
from Internship.gemini_resume_VLSI_intern import resume_analysis_VLSI_Intern
from Placement.gemini_resume_CSE_placement import resume_analysis_CSE_Placement
from Placement.gemini_resume_Analytics_placement import resume_analysis_Analytics_Placement
from Placement.gemini_resume_BM_placement import resume_analysis_BM_Placement
from Placement.gemini_resume_BT_placement import resume_analysis_BT_Placement
from Placement.gemini_resume_CE_placement import resume_analysis_CE_Placement
from Placement.gemini_resume_CH_placement import resume_analysis_CH_Placement
from Placement.gemini_resume_CR_placement import resume_analysis_CR_Placement
from Placement.gemini_resume_ECE_placement import resume_analysis_ECE_Placement
from Placement.gemini_resume_EI_placement import resume_analysis_EI_Placement
from Placement.gemini_resume_FP_placement import resume_analysis_FP_Placement
from Placement.gemini_resume_ID_placement import resume_analysis_ID_Placement
from Placement.gemini_resume_ME_placement import resume_analysis_ME_Placement
from Placement.gemini_resume_MN_placement import resume_analysis_MN_Placement
from Placement.gemini_resume_MT_placement import resume_analysis_MT_Placement
from Placement.gemini_resume_VLSI_placement import resume_analysis_VLSI_Placement
from Placement.gemini_resume_Analytics_placement import resume_analysis_Analytics_Placement 


app = FastAPI()

# Allow requests from your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify ["http://localhost:3000"]
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResumeData(BaseModel):
    resume_text: str
    position_type: str
    field: str

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    position_type: str = Form(...),
    field: str = Form(...)
):
    try:
        # Read and extract text from uploaded file
        file_bytes = await file.read()
        resume_text = extract_text_from_pdf(file_bytes)

        # Generate analysis using Gemini
       #analysis = resume_analysis_CSE_Intern(
            #resume_text=resume_text,
            #position_type=position_type,
            #field=field
        #)
        analysis=""
        if(position_type == "Intern"):
            if(field == "Software/IT"):
                analysis = resume_analysis_CSE_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Analytics"):
                analysis = resume_analysis_Analytics_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Biomedical"):
                analysis = resume_analysis_BM_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Biotechnology"):
                analysis = resume_analysis_BT_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Civil"):
                analysis = resume_analysis_CE_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Chemical"):
                analysis = resume_analysis_CH_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Ceramic"):
                analysis = resume_analysis_CR_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Electronics & Communication"):
                analysis = resume_analysis_ECE_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Electrical"):
                analysis = resume_analysis_EE_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Electronics & Instrumentation"):
                analysis = resume_analysis_EI_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Food Processing"):
                analysis = resume_analysis_FP_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Industrial Design"):
                analysis = resume_analysis_ID_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Mechanical"):
                analysis = resume_analysis_ME_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Mining"):
                analysis = resume_analysis_MN_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "Metallurgy"):
                analysis = resume_analysis_MT_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field == "VLSI"):
                analysis = resume_analysis_VLSI_Intern(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
        elif(position_type == "Placement"):
            if(field=="Software/IT"):
                analysis=resume_analysis_CSE_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Analytics"):
                analysis=resume_analysis_Analytics_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Biomedical"):
                analysis=resume_analysis_BM_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Biotechnology"):
                analysis=resume_analysis_BT_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Civil"):
                analysis=resume_analysis_CE_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Chemical"):
                analysis=resume_analysis_CH_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Ceramic"):
                analysis=resume_analysis_CR_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Electronics & Communication"):
                analysis=resume_analysis_ECE_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Electronics & Instrumentation"):
                analysis=resume_analysis_EI_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Food Processing"):
                analysis=resume_analysis_FP_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Industrial Design"):
                analysis=resume_analysis_ID_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Mechanical"):
                analysis=resume_analysis_ME_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Mining"):
                analysis=resume_analysis_MN_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="Metallurgy"):
                analysis=resume_analysis_MT_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
            elif(field=="VLSI"):
                analysis=resume_analysis_VLSI_Placement(
                    resume_text=resume_text,
                    position_type=position_type,
                    field=field
                )
        return {"result": analysis}

    except Exception as e:
        print("🔥 Error during analysis:", str(e))
        return {"error": "Internal server error"}, 500