const router = require('express').Router();
const { signupValidation,loginValidation } = require('../middlewares/authValidation');
const { signup,login } = require('../Controller/authController');

router.post('/login',loginValidation, login);
router.post('/signup',signupValidation, signup);

module.exports = router;