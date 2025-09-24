// routes/resumeRoutes.js
import express from "express";
import multer from "multer";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";

const router = express.Router();
const upload = multer({ dest: "uploads/" });

router.post("/upload", upload.single("resume"), async (req, res) => {
  const filePath = path.resolve(req.file.path);

  // Call Python script
  const python = spawn("python", ["resume_parser.py", filePath]);

  let data = "";
  python.stdout.on("data", (chunk) => {
    data += chunk.toString();
  });

  python.stderr.on("data", (err) => {
    console.error("Python error:", err.toString());
  });

  python.on("close", (code) => {
    fs.unlinkSync(filePath); // Cleanup temp file

    if (code !== 0) {
      return res.status(500).json({ error: "Python script failed" });
    }

    try {
      const parsed = JSON.parse(data);
      res.json(parsed);
    } catch (err) {
      res.status(500).json({ error: "Failed to parse output", detail: err.message });
    }
  });
});

export default router;
