const express = require("express");
const axios = require("axios");
const router = express.Router();

router.post("/analyze-resume", async (req, res) => {
  try {
    const { resumeText, positionType, field } =
      req.body;

    const response = await axios.post("http://localhost:8000/analyze", {
      resume_text: resumeText,
      position_type: positionType,
      field: field
    });

    res.json({ result: response.data.result });
  } catch (error) {
    console.error("Error analyzing resume:", error);
    res.status(500).json({ error: "Failed to analyze resume" });
  }
});

module.exports = router;
