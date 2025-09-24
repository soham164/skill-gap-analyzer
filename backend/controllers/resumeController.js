import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from "url";

// emulate __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const parseResume = (req, res) => {
    const resumePath = req.file.path;

    const python = spawn('python', [path.join(__dirname, '../resume_parser.py'), resumePath]);

    let result = '';
    let error = '';

    python.stdout.on('data', (data) => {
        result += data.toString();
    });

    python.stderr.on('data', (data) => {
        error += data.toString();
    });

    python.on('close', (code) => {
        if (code !== 0 || error) {
            return res.status(500).json({
                error: "Resume parsing failed",
                detail: error || "Unknown error"
            });
        }
        try {
            return res.status(200).json(JSON.parse(result));
        } catch (e) {
            return res.status(500).json({
                error: "Failed to parse JSON from resume_parser.py",
                detail: e.message
            });
        }
    });
};
