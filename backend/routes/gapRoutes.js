import express from "express";
import axios from "axios";

const router = express.Router();

// POST /api/skill-gap/analyze
router.post("/analyze", async (req, res) => {
  try {
    // forward request body to Python FastAPI
    const response = await axios.post("http://localhost:8000/analyze", req.body);

    res.json(response.data); // return Python’s response to frontend
  } catch (error) {
    console.error("Error connecting to Python service:", error.message);
    res.status(500).json({ error: "Skill gap analysis service unavailable" });
  }
});

export default router;
