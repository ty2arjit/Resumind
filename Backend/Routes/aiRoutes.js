const express = require("express");
const axios = require("axios");
const multer = require("multer");
const FormData = require("form-data");
const router = express.Router();

const upload = multer({ storage: multer.memoryStorage() });

const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000";

router.post("/analyze-resume", upload.single("resume"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "No resume file uploaded" });
    }

    const { positionType, field } = req.body;

    const formData = new FormData();
    formData.append("file", req.file.buffer, req.file.originalname);
    formData.append("position_type", positionType);
    formData.append("field", field);

    const response = await axios.post(`${FASTAPI_URL}/analyze`, formData, {
      headers: formData.getHeaders(),
    });

    res.json({ result: response.data.result });
  } catch (error) {
    console.error("Error analyzing resume:", error);
    res.status(500).json({ error: "Failed to analyze resume" });
  }
});

module.exports = router;