const prisma = require("../config/prismaClient");
const bcrypt = require('bcrypt')
const jwt = require("jsonwebtoken");
require('dotenv').config();

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
    console.error("Signup error:", err);
    res.status(500).json({message: "Internal server error", success: false});
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
    res.status(500).json({message: "Internal server error", success: false});
  }
}

module.exports = {
  signup,
  login
}
