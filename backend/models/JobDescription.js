import mongoose from "mongoose";

const jobSchema = new mongoose.Schema({
  userId: mongoose.Schema.Types.ObjectId,
  requiredSkills: [String],
  description: String,
});

export default mongoose.model("JobDescription", jobSchema);