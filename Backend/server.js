const http = require("http");
const express = require("express");
const cors = require("cors");
const multer = require("multer");
const path = require("path");
const aiRoute = require('./Routes/aiRoutes');
const bodyParser = require('body-parser');
const authRouter = require('./Routes/authRoutes')
require('./Models/db');
require('dotenv').config(); 
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors({
  origin: ["http://localhost:5173", "https://resumind-recovery.vercel.app", "https://resumind-recovery-git-main-ty2arjit.vercel.app"],
  credentials: true
}));
app.use(express.json());
app.use("/uploads", express.static("uploads"));
app.use("/auth", authRouter);
app.use("/api", aiRoute);
app.use(bodyParser.json());


const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'Uploads');
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + file.originalname);
  }
});

const fileFilter = (req, file, cb) => {
  if(req.mimetype === 'application/pdf') {
    cb(null, true);
  }
  else{
    cb(new Error('Only PDF files are allowed!'), false);
  }
}

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: 5 * 1024 * 1024
  } // limit: 5MB
})

// Upload API
app.post('/Upload', upload.single('resume'), (req, res) => {
  if(!req.file) {
    return res.status(400).json(
      { error: 'No file uploaded or invalid file format'}
    )
  }
  res.status(200).json({
    message: 'File uploaded successfully',
    filePath: req.file.path,
    fileName: req.file.filename
  })
})


app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});