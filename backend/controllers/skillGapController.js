import axios from "axios";

export const analyzeSkillGap = async (req, res) => {
  try {
    const { resumeText, jobDescription } = req.body;

    const response = await axios.post("http://localhost:8000/analyze", {
      resume_text: resumeText,
      job_description: jobDescription,
    });

    res.json(response.data);
  } catch (error) {
    console.error("Skill gap analysis error:", error.message);
    res.status(500).json({ message: "Skill gap analysis failed" });
  }
};
