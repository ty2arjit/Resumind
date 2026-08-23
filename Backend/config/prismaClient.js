const { PrismaClient } = require('../generated/prisma');
const { PrismaPg } = require('@prisma/adapter-pg');
require('dotenv').config();

const connectionString = process.env.POSTGRESQL_DATABASE_URL;

if (!connectionString) {
  throw new Error(
    'POSTGRESQL_DATABASE_URL is not set. Add your Neon connection string to Backend/.env.'
  );
}

const adapter = new PrismaPg({
  connectionString,
  connectionTimeoutMillis: 10000,
});

const prisma = new PrismaClient({ adapter });

module.exports = prisma;
