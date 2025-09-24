import Job from "../models/JobDescription.js";
import { extractSkills } from "../utils/skillExtractor.js";

export const analyzeJob = async (req, res) => {
  const { description } = req.body;
  const requiredSkills = extractSkills(description);

  const job = new Job({
    userId: req.user._id,
    requiredSkills,
    description,
  });

  await job.save();
  res.status(200).json({ requiredSkills });
};