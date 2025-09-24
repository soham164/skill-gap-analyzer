import express from "express";
import axios from "axios";

const router = express.Router();

router.post("/analyze-skill-gap", async (req, res) => {
  const { resumeText, jobText } = req.body;
  try {
    // Forward to Python FastAPI service
    const response = await axios.post("http://localhost:8000/api/skill-gap/analyze-json", {
      resume_text: resumeText,
      job_text: jobText,
      strategy: "hybrid",
      detailed: false
    });
    res.json(response.data);
  } catch (err) {
    console.error("Error connecting to Python AI service:", err.message);
    res.status(500).json({ error: "AI service unavailable" });
  }
});

// Extract skills from text
router.post("/extract-skills", async (req, res) => {
  const { text, strategy = "hybrid" } = req.body;
  try {
    const response = await axios.post("http://localhost:8000/api/skills/extract", {
      text: text,
      strategy: strategy
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    res.json(response.data);
  } catch (err) {
    console.error("Error extracting skills:", err.message);
    res.status(500).json({ error: "Skill extraction service unavailable" });
  }
});

// Get skill recommendations
router.post("/recommendations", async (req, res) => {
  const { skills, currentLevel = "beginner", timeAvailable = "3-6 months" } = req.body;
  try {
    const response = await axios.post("http://localhost:8000/api/recommendations/generate", {
      skills: skills,
      current_level: currentLevel,
      time_available: timeAvailable
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    res.json(response.data);
  } catch (err) {
    console.error("Error getting recommendations:", err.message);
    res.status(500).json({ error: "Recommendations service unavailable" });
  }
});

export default router;
