// models/Job.js
import mongoose from "mongoose";

const JobSchema = new mongoose.Schema({
  title: { type: String, required: true },
  description: { type: String, required: true },
  requiredSkills: [String], // extracted skills
  company: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true }, // who posted
  applicants: [{ type: mongoose.Schema.Types.ObjectId, ref: "User" }] // people who applied
}, { timestamps: true });

export default mongoose.model("Job", JobSchema);
