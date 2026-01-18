const router = require('express').Router();
const { signupValidation,loginValidation } = require('../middleware/AuthValidation');
const { signup,login } = require('../Controller/AuthController');

router.post('/login',loginValidation, login);
router.post('/signup',signupValidation, signup);

module.exports = router;