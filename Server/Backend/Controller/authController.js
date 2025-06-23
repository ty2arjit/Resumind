const User = require("../Models/User");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const express = require("express");
import dotenv from 'dotenv';

dotenv.config();
const router = express.Router();
const JWT_Key = process.env.JWT_KEY;


// Sign Up Route
router.post("/signup", async (req, res) => {
  const {name, email, password} = req.body;

  try {
    const existingUser = await User.findOne({ email });
    if(existingUser){
      return res.status(400).json({ error: "User already exists" })
    }
    const hashedPassword = await bcrypt.hash(password,10)
    const newUser = await User.create({
      name,
      email,
      password: hashedPassword,
    });

    res.status(201).json({
      message: "User created Successfully",
      user: newUser,
    });
  } catch (err) {
    res.status(500).json({ error: "Server error "});
  }
});

// Sign in Route

router.post("/signin", async (req, res) => {
  const {email, password} = req.body;

  try {
    const user = await User.findOne({email});
    if(!user) {
      return res.status(400).json({
        error: "Invalid Credentials"
      })
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if(!isMatch) {
      return res.status(400).json({
        error: "Invalid Password"
      })
    }
    const token = jwt.sign(
      { id: user._id},
      JWT_Key,
      {
        expiresIn: "1d",     
      }
    );

    res.status(200).json({
      message: "Logged in Successfully",
      token,
      user,
    })
  } catch (err) {
    res.status(500).json({ error: "Server error "});
  }
})

export default router;
