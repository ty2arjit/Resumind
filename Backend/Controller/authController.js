const prisma = require("../config/prismaClient");
const bcrypt = require('bcrypt')
const jwt = require("jsonwebtoken");
require('dotenv').config();

// Connection-level failures (timeout, DNS, refused, Neon auto-suspend
// wake-up taking too long) look identical to any other 500 from the
// client's perspective otherwise, which makes them impossible to
// self-diagnose. Surface them distinctly instead.
const isDbConnectivityError = (err) =>
  err?.code === 'P1001' || // Prisma: can't reach database server
  err?.code === 'P1002' || // Prisma: database server timed out
  /connection.*(timeout|terminated|refused)/i.test(err?.message || '') ||
  /connection.*(timeout|terminated|refused)/i.test(err?.cause?.message || '');

const handleAuthError = (res, err, action) => {
  console.error(`${action} error:`, err);
  if (isDbConnectivityError(err)) {
    return res.status(503).json({
      message: 'Could not reach the database. Check that POSTGRESQL_DATABASE_URL in Backend/.env is correct and that your Neon project is active (not paused).',
      success: false,
    });
  }
  res.status(500).json({ message: 'Internal server error', success: false });
};

const signup = async(req, res) => {
  try {
    const { name,college,email,password } = req.body;
    const existing = await prisma.user.findUnique({ where: { email } });
    if( existing ) {
      return res.status(400).json({message: "User already exists", success: false});
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    await prisma.user.create({
      data: { name, college, email, password: hashedPassword }
    });

    res.status(201).json({message: "Signed up successfully", success: true});
  } catch (err) {
    handleAuthError(res, err, 'Signup');
  }
}

const login = async(req, res) => {
  try {
    const { email, password } = req.body;
    const user = await prisma.user.findUnique({ where: { email } });
    if( !user ) {
      return res.status(400).json({message: "User not found", success: false});
    }
    const check = await bcrypt.compare(password, user.password);
    if( !check ) {
      return res.status(400).json({message: "Incorrect password", success: false});
    }

    const jwtToken = jwt.sign(
      {email: user.email, _id: user.id},
      process.env.JWT_KEY,
      {expiresIn: '24h'}
    );

    res.status(200).json({message: "Logged in successfully",
      success: true,
      jwtToken,
      email,
      name: user.name
    });


  } catch (err) {
    handleAuthError(res, err, 'Login');
  }
}

module.exports = {
  signup,
  login
}
