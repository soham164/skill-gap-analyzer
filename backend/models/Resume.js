import mongoose from "mongoose";

const resumeSchema = new mongoose.Schema({
  userId: mongoose.Schema.Types.ObjectId,
  skills: [String],
  parsedText: String,
});

export default mongoose.model("Resume", resumeSchema);