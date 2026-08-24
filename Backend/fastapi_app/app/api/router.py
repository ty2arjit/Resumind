from fastapi import APIRouter

from app.api import health, jobs, resume_quality, resumes

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(resumes.router)
api_router.include_router(jobs.router)
api_router.include_router(resume_quality.router)
