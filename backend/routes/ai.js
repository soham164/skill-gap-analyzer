const express = require("express");
const axios = require("axios");
const router = express.Router();

router.post("/analyze-skill-gap", async (req, res) => {
  const { resumeText, jobText } = req.body;
  try {
    const response = await axios.post("http://localhost:5400/analyze-skill-gap", {
      resume: resumeText,
      job: jobText,
    });
    res.json(response.data); // forward response to frontend
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "AI service unavailable" });
  }
});

module.exports = router;
