-- Adds the password column needed for the auth cutover from MongoDB to
-- Postgres. Assumes the `users` table is still empty (the app has not had
-- working Postgres-backed auth until now) — if it already has rows without
-- a password, this will fail and needs a backfill first.
ALTER TABLE "users" ADD COLUMN "password" TEXT NOT NULL;
