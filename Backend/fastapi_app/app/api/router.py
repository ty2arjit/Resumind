from fastapi import APIRouter

from app.api import analysis, health, jobs, resume_quality, resumes, target_profiles

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(resumes.router)
api_router.include_router(jobs.router)
api_router.include_router(resume_quality.router)
api_router.include_router(target_profiles.router)
api_router.include_router(analysis.router)
