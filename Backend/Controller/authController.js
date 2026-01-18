const userModel = require("../Models/User")
const bcrypt = require('bcrypt')
const jwt = require("jsonwebtoken");
require('dotenv').config();

const signup = async(req, res) => {
  try {
    const { name,college,email,password } = req.body;
    const search = await userModel.findOne({email});
    if( search ) {
      res.status(400).json({message: "User already exists", sucess: false});
    }

    const user = new userModel({name, college, email, password});
    user.password = await bcrypt.hash(password, 10);
    await user.save();

    res.status(201).json({message: "Signed up sucessfully", success:true});
  } catch (err) {
    res.status(500).json({message: "Interal server error", success: false, err});
  }
}

const login = async(req, res) => {
  try {
    const { email, password } = req.body;
    const user = userModel({email});
    if( !user ) {
      res.status(400).json({message: "User not found", success: false});
    }
    const check = await bcrypt.compare(password, user.password);
    if( !check ) {
      return res.status(400).json({message: "Incorrect password", success: false});
    }

    const jwtToken = jwt.sign(
      {email: user.email, _id: user._id},
      process.env.JWT_KEY,
      {expiresIn: '24h'}
    );

    res.status(200).json({message: "Logged in successfully",
      success: true,
      jwtToken,
      email
    });


  } catch (err) {
    res.status(500).json({message: "Internal server error", success: false});
  }
}

module.exports = {
  signup,
  login
}