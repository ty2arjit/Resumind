const Joi = require('joi');

const signupValidation = (req, res, next) => {
  const schema = Joi.object({
    name: Joi.string().required(),
    college: Joi.string(),
    email: Joi.string().email().required(),
    password: Joi.string().required()
  });

  const {error} = schema.validate(req.body);
  if(error) {
    res.status(400).json({message: "Bad request", error});
  }
  next();
};

const loginValidation = (req, res, next) => {
  const schema = Joi.object({
    email: Joi.string().email().required(),
    password: Joi.string().required()
  })

  const { error } = schema.validate(req.body);
  if(error) {
    res.status(400).json({message: "Bad credentials", error});
  }
  next();
}

module.exports = {
  signupValidation,
  loginValidation
}