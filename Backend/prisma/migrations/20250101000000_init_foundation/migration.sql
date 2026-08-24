-- Enable pgcrypto for gen_random_uuid() used as the default id generator
-- across all Phase 1 tables (works regardless of which ORM inserts the row).
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateEnum
CREATE TYPE "requirement_type" AS ENUM ('SKILL', 'RESPONSIBILITY', 'EXPERIENCE', 'QUALIFICATION', 'PREFERRED_SKILL', 'DOMAIN_KNOWLEDGE', 'OTHER');

-- CreateEnum
CREATE TYPE "importance_level" AS ENUM ('REQUIRED', 'PREFERRED', 'OPTIONAL', 'UNKNOWN');

-- CreateEnum
CREATE TYPE "match_strength" AS ENUM ('MISSING', 'WEAK', 'PARTIAL', 'STRONG', 'VERY_STRONG', 'UNKNOWN');

-- CreateEnum
CREATE TYPE "analysis_mode" AS ENUM ('JD', 'TARGET_PROFILE', 'COMBINED');

-- CreateEnum
CREATE TYPE "analysis_status" AS ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED');

-- CreateEnum
CREATE TYPE "document_source_type" AS ENUM ('PDF', 'DOCX', 'TEXT');

-- CreateTable
CREATE TABLE "users" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "mongo_user_id" TEXT,
    "email" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "college" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "resumes" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "title" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "resumes_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "resume_versions" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "resume_id" UUID NOT NULL,
    "version_number" INTEGER NOT NULL,
    "source_filename" TEXT,
    "source_type" "document_source_type" NOT NULL DEFAULT 'PDF',
    "raw_text" TEXT,
    "structured_data" JSONB,
    "parser_version" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "resume_versions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "job_descriptions" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "title" TEXT,
    "company" TEXT,
    "source_type" "document_source_type" NOT NULL DEFAULT 'TEXT',
    "source_filename" TEXT,
    "raw_text" TEXT NOT NULL,
    "structured_data" JSONB,
    "parser_version" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "job_descriptions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "target_profiles" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID,
    "is_system" BOOLEAN NOT NULL DEFAULT false,
    "position" TEXT NOT NULL,
    "domain" TEXT,
    "profile_version" TEXT NOT NULL DEFAULT 'v1',
    "profile_data" JSONB,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "target_profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "analyses" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "resume_version_id" UUID NOT NULL,
    "job_description_id" UUID,
    "target_profile_id" UUID,
    "mode" "analysis_mode" NOT NULL,
    "status" "analysis_status" NOT NULL DEFAULT 'PENDING',
    "algorithm_version" TEXT,
    "scoring_config_version" TEXT,
    "embedding_model_version" TEXT,
    "ats_alignment_score" DOUBLE PRECISION,
    "resume_quality_score" DOUBLE PRECISION,
    "target_fit_score" DOUBLE PRECISION,
    "error_message" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMPTZ,

    CONSTRAINT "analyses_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "requirements" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "job_description_id" UUID,
    "target_profile_id" UUID,
    "text" TEXT NOT NULL,
    "type" "requirement_type" NOT NULL,
    "canonical_entity" TEXT,
    "importance" "importance_level" NOT NULL DEFAULT 'UNKNOWN',
    "critical" BOOLEAN NOT NULL DEFAULT false,
    "weight" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "confidence" DOUBLE PRECISION,
    "source_section" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "requirements_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "requirement_matches" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "analysis_id" UUID NOT NULL,
    "requirement_id" UUID NOT NULL,
    "match_strength" "match_strength" NOT NULL DEFAULT 'UNKNOWN',
    "score" DOUBLE PRECISION,
    "keyword_signal" DOUBLE PRECISION,
    "semantic_signal" DOUBLE PRECISION,
    "evidence_signal" DOUBLE PRECISION,
    "context_signal" DOUBLE PRECISION,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "requirement_matches_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "evidence" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "requirement_match_id" UUID NOT NULL,
    "text" TEXT NOT NULL,
    "section" TEXT,
    "position" TEXT,
    "technologies" JSONB,
    "actions" JSONB,
    "objects" JSONB,
    "metrics" JSONB,
    "relevance_score" DOUBLE PRECISION,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "evidence_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "recommendations" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "analysis_id" UUID NOT NULL,
    "text" TEXT NOT NULL,
    "category" TEXT,
    "priority" INTEGER,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "recommendations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "score_breakdowns" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "analysis_id" UUID NOT NULL,
    "category" TEXT NOT NULL,
    "score" DOUBLE PRECISION NOT NULL,
    "weight" DOUBLE PRECISION NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "score_breakdowns_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "evaluation_cases" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "name" TEXT NOT NULL,
    "job_description_text" TEXT NOT NULL,
    "resume_text" TEXT NOT NULL,
    "ground_truth" JSONB NOT NULL,
    "human_overall_score" DOUBLE PRECISION,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "evaluation_cases_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "evaluation_results" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "evaluation_case_id" UUID NOT NULL,
    "algorithm_version" TEXT NOT NULL,
    "metrics" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "evaluation_results_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_mongo_user_id_key" ON "users"("mongo_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE INDEX "resumes_user_id_idx" ON "resumes"("user_id");

-- CreateIndex
CREATE INDEX "resume_versions_resume_id_idx" ON "resume_versions"("resume_id");

-- CreateIndex
CREATE UNIQUE INDEX "resume_versions_resume_id_version_number_key" ON "resume_versions"("resume_id", "version_number");

-- CreateIndex
CREATE INDEX "job_descriptions_user_id_idx" ON "job_descriptions"("user_id");

-- CreateIndex
CREATE INDEX "target_profiles_user_id_idx" ON "target_profiles"("user_id");

-- CreateIndex
CREATE INDEX "target_profiles_position_domain_idx" ON "target_profiles"("position", "domain");

-- CreateIndex
CREATE INDEX "analyses_user_id_idx" ON "analyses"("user_id");

-- CreateIndex
CREATE INDEX "analyses_resume_version_id_idx" ON "analyses"("resume_version_id");

-- CreateIndex
CREATE INDEX "requirements_job_description_id_idx" ON "requirements"("job_description_id");

-- CreateIndex
CREATE INDEX "requirements_target_profile_id_idx" ON "requirements"("target_profile_id");

-- CreateIndex
CREATE INDEX "requirement_matches_analysis_id_idx" ON "requirement_matches"("analysis_id");

-- CreateIndex
CREATE INDEX "requirement_matches_requirement_id_idx" ON "requirement_matches"("requirement_id");

-- CreateIndex
CREATE UNIQUE INDEX "requirement_matches_analysis_id_requirement_id_key" ON "requirement_matches"("analysis_id", "requirement_id");

-- CreateIndex
CREATE INDEX "evidence_requirement_match_id_idx" ON "evidence"("requirement_match_id");

-- CreateIndex
CREATE INDEX "recommendations_analysis_id_idx" ON "recommendations"("analysis_id");

-- CreateIndex
CREATE INDEX "score_breakdowns_analysis_id_idx" ON "score_breakdowns"("analysis_id");

-- CreateIndex
CREATE INDEX "evaluation_results_evaluation_case_id_idx" ON "evaluation_results"("evaluation_case_id");

-- AddForeignKey
ALTER TABLE "resumes" ADD CONSTRAINT "resumes_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "resume_versions" ADD CONSTRAINT "resume_versions_resume_id_fkey" FOREIGN KEY ("resume_id") REFERENCES "resumes"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "job_descriptions" ADD CONSTRAINT "job_descriptions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "target_profiles" ADD CONSTRAINT "target_profiles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analyses" ADD CONSTRAINT "analyses_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analyses" ADD CONSTRAINT "analyses_resume_version_id_fkey" FOREIGN KEY ("resume_version_id") REFERENCES "resume_versions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analyses" ADD CONSTRAINT "analyses_job_description_id_fkey" FOREIGN KEY ("job_description_id") REFERENCES "job_descriptions"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "analyses" ADD CONSTRAINT "analyses_target_profile_id_fkey" FOREIGN KEY ("target_profile_id") REFERENCES "target_profiles"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "requirements" ADD CONSTRAINT "requirements_job_description_id_fkey" FOREIGN KEY ("job_description_id") REFERENCES "job_descriptions"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "requirements" ADD CONSTRAINT "requirements_target_profile_id_fkey" FOREIGN KEY ("target_profile_id") REFERENCES "target_profiles"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "requirement_matches" ADD CONSTRAINT "requirement_matches_analysis_id_fkey" FOREIGN KEY ("analysis_id") REFERENCES "analyses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "requirement_matches" ADD CONSTRAINT "requirement_matches_requirement_id_fkey" FOREIGN KEY ("requirement_id") REFERENCES "requirements"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "evidence" ADD CONSTRAINT "evidence_requirement_match_id_fkey" FOREIGN KEY ("requirement_match_id") REFERENCES "requirement_matches"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "recommendations" ADD CONSTRAINT "recommendations_analysis_id_fkey" FOREIGN KEY ("analysis_id") REFERENCES "analyses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "score_breakdowns" ADD CONSTRAINT "score_breakdowns_analysis_id_fkey" FOREIGN KEY ("analysis_id") REFERENCES "analyses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "evaluation_results" ADD CONSTRAINT "evaluation_results_evaluation_case_id_fkey" FOREIGN KEY ("evaluation_case_id") REFERENCES "evaluation_cases"("id") ON DELETE CASCADE ON UPDATE CASCADE;

