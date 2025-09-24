// src/pages/PostJob.jsx
import React, { useState } from "react";

const PostJob = () => {
  const [companyName, setCompanyName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [description, setDescription] = useState("");
  const [jobs, setJobs] = useState(() => {
    const stored = localStorage.getItem("jobs");
    return stored ? JSON.parse(stored) : [];
  });

  const handlePostJob = (e) => {
    e.preventDefault();
    if (!companyName || !jobTitle || !description) {
      alert("All fields are required!");
      return;
    }

    const newJob = { id: Date.now(), companyName, jobTitle, description };
    const updatedJobs = [...jobs, newJob];
    setJobs(updatedJobs);
    localStorage.setItem("jobs", JSON.stringify(updatedJobs));

    setCompanyName("");
    setJobTitle("");
    setDescription("");
    alert("Job posted successfully!");
  };

  const handleDeleteJob = (id) => {
    const updatedJobs = jobs.filter((job) => job.id !== id);
    setJobs(updatedJobs);
    localStorage.setItem("jobs", JSON.stringify(updatedJobs));
    alert("Job deleted successfully!");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 flex flex-col items-center justify-start p-6">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-lg border border-gray-100 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Post a Job</h2>
        <form onSubmit={handlePostJob} className="space-y-4">
          <input
            type="text"
            placeholder="Company Name"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg"
            required
          />
          <input
            type="text"
            placeholder="Job Title"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg"
            required
          />
          <textarea
            placeholder="Job Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg"
            rows="5"
            required
          ></textarea>
          <button
            type="submit"
            className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 w-full"
          >
            Post Job
          </button>
        </form>
      </div>

      {/* Posted Jobs List */}
      <div className="w-full max-w-2xl bg-white p-6 rounded-2xl shadow-md border border-gray-100">
        <h3 className="text-xl font-semibold mb-4">Posted Jobs</h3>
        {jobs.length === 0 ? (
          <p className="text-gray-500">No jobs posted yet.</p>
        ) : (
          <ul className="space-y-4">
            {jobs.map((job) => (
              <li
                key={job.id}
                className="p-4 border rounded-lg flex justify-between items-start bg-gray-50"
              >
                <div>
                  <h4 className="font-bold text-gray-800">{job.jobTitle}</h4>
                  <p className="text-sm text-gray-600">{job.companyName}</p>
                  <p className="text-gray-700 mt-1">{job.description}</p>
                </div>
                <button
                  onClick={() => handleDeleteJob(job.id)}
                  className="ml-4 bg-red-500 text-white px-3 py-1 rounded-lg hover:bg-red-600"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default PostJob;
