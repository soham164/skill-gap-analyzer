// src/pages/AnalyzeSkills.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";

const AnalyzeSkills = () => {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState("");
  const [jobText, setJobText] = useState("");
  const [resume, setResume] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // 🔹 Sync jobs with localStorage
  useEffect(() => {
    const loadJobs = () => {
      const storedJobs = localStorage.getItem("jobs");
      if (storedJobs) {
        setJobs(JSON.parse(storedJobs));
      }
    };

    loadJobs();
    window.addEventListener("storage", loadJobs);

    return () => window.removeEventListener("storage", loadJobs);
  }, []);

  const handleFileChange = (e) => {
    setResume(e.target.files[0]);
  };

  const handleAnalyze = async () => {
    if (!resume) return alert("Please upload your resume first!");
    if (!selectedJob && !jobText) {
      return alert("Select a job OR paste a job description!");
    }

    // If user selected a job, use its description
    let finalJobText = jobText;
    if (selectedJob) {
      const job = jobs.find((j) => j.id.toString() === selectedJob);
      if (job) finalJobText = job.description;
    }

    const formData = new FormData();
    formData.append("file", resume);
    formData.append("job_text", finalJobText);

    try {
      setLoading(true);
      const res = await axios.post(
        "http://localhost:8000/api/skill-gap/analyze",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Skill gap analysis failed. Check if backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-4 text-gray-800">Analyze Skills</h1>

      <div className="bg-white p-6 rounded-xl shadow-md space-y-4">
        {/* 🔹 Resume Upload */}
        <label className="block text-sm font-medium text-gray-700">
          Upload Resume (PDF)
        </label>
        <input type="file" accept="application/pdf" onChange={handleFileChange} />

        {/* 🔹 Select Job Dropdown */}
        <label className="block text-sm font-medium text-gray-700">
          Select a Posted Job (optional)
        </label>
        <select
          value={selectedJob}
          onChange={(e) => {
            const jobId = e.target.value;
            setSelectedJob(jobId);

            const job = jobs.find((j) => j.id.toString() === jobId);
            if (job) setJobText(job.description); // auto-fill JD
          }}
          className="w-full border rounded px-3 py-2"
        >
          <option value="">-- Select a Job --</option>
          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              {job.companyName} - {job.jobTitle}
            </option>
          ))}
        </select>

        {/* 🔹 Job Description Textarea */}
        <label className="block text-sm font-medium text-gray-700">
          Job Description (auto-filled if job selected)
        </label>
        <textarea
          className="w-full border rounded px-3 py-2"
          rows={5}
          value={jobText}
          onChange={(e) => setJobText(e.target.value)}
        />

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>

        {/* 🔹 Results */}
        {result && (
          <div className="mt-6 space-y-6">
            {/* Matched Skills */}
            <div>
              <h2 className="font-semibold text-green-600 mb-2">
                ✅ Matched Skills ({(result.matched_skills || result.matched)?.length || 0})
              </h2>
              <div className="flex flex-wrap gap-2">
                {(result.matched_skills || result.matched || []).map((skill) => (
                  <span
                    key={skill}
                    className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Missing Skills */}
            <div>
              <h2 className="font-semibold text-red-600 mb-2">
                ❌ Missing Skills ({(result.missing_skills || result.missing)?.length || 0})
              </h2>
              <div className="flex flex-wrap gap-2">
                {(result.missing_skills || result.missing || []).map((skill) => (
                  <span
                    key={skill}
                    className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Additional Skills */}
            {((result.additional_skills || result.additional) &&
              (result.additional_skills || result.additional).length > 0) && (
              <div>
                <h2 className="font-semibold text-blue-600 mb-2">
                  ➕ Additional Skills ({(result.additional_skills || result.additional).length})
                </h2>
                <div className="flex flex-wrap gap-2">
                  {(result.additional_skills || result.additional).map((skill) => (
                    <span
                      key={skill}
                      className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            <div>
              <h2 className="font-semibold text-purple-600 mb-4">
                📘 Learning Recommendations
              </h2>
              <div className="space-y-4">
                {Object.entries(result.recommendations || {}).map(([skill, rec]) => (
                  <div key={skill} className="bg-gray-50 p-4 rounded-lg border">
                    <h3 className="font-medium text-gray-800 mb-2">🎯 {skill}</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <div className="mb-2">
                          <span className="text-sm text-gray-600">Difficulty: </span>
                          <span className="font-medium text-orange-600">
                            {rec.difficulty}
                          </span>
                        </div>
                        <div className="mb-3">
                          <span className="text-sm text-gray-600">Time Estimate: </span>
                          <span className="font-medium text-blue-600">
                            {rec.time_estimate}
                          </span>
                        </div>
                        {rec.related_skills?.length > 0 && (
                          <div>
                            <p className="text-sm font-medium text-gray-700 mb-1">
                              Related Skills:
                            </p>
                            <div className="flex flex-wrap gap-1">
                              {rec.related_skills.map((relatedSkill, idx) => (
                                <span
                                  key={idx}
                                  className="bg-gray-200 text-gray-700 px-2 py-1 rounded text-xs"
                                >
                                  {relatedSkill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-2">
                          Learning Resources:
                        </p>
                        <ul className="space-y-1">
                          {rec.courses?.map((course, idx) => (
                            <li key={idx} className="text-sm text-gray-600 flex items-start">
                              <span className="text-indigo-500 mr-2">•</span>
                              <span>{course}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Summary Stats */}
            <div className="bg-indigo-50 p-4 rounded-lg">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-indigo-600">
                    {result.match_percentage || 0}%
                  </p>
                  <p className="text-sm text-gray-600">Match Rate</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-600">
                    {(result.matched_skills || result.matched || []).length}
                  </p>
                  <p className="text-sm text-gray-600">Matched</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-red-600">
                    {(result.missing_skills || result.missing || []).length}
                  </p>
                  <p className="text-sm text-gray-600">Missing</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-blue-600">
                    {(result.additional_skills || result.additional).length}
                  </p>
                  <p className="text-sm text-gray-600">Additional</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyzeSkills;


