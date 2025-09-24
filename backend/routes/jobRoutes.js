// routes/jobRoutes.js
import express from "express";
import Job from "../models/Job.js";
import { protect } from "../middleware/authMiddleware.js";

const router = express.Router();

// ✅ Create job (company side)
router.post("/", protect, async (req, res) => {
  try {
    const job = new Job({ ...req.body, company: req.user.id });
    await job.save();
    res.json(job);
  } catch (err) {
    res.status(500).json({ message: "Job creation failed" });
  }
});

// ✅ Get all jobs
router.get("/", async (req, res) => {
  const jobs = await Job.find().populate("company", "name email");
  res.json(jobs);
});

// ✅ Apply to a job
router.post("/:jobId/apply", protect, async (req, res) => {
  const job = await Job.findById(req.params.jobId);
  if (!job) return res.status(404).json({ message: "Job not found" });

  if (!job.applicants.includes(req.user.id)) {
    job.applicants.push(req.user.id);
    await job.save();
  }
  res.json({ message: "Applied successfully" });
});

export default router;
