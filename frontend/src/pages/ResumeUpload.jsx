// src/pages/ResumeUpload.jsx
import React, { useState } from "react";

const ResumeUpload = () => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = (e) => {
    e.preventDefault();
    if (file) {
      console.log("Resume selected:", file.name);
      // You’ll implement parsing/upload logic later
    }
  };

  return (
    <div className="p-8 max-w-xl mx-auto bg-white rounded-2xl shadow-md mt-8">
      <h2 className="text-2xl font-bold mb-4">Upload Your Resume</h2>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept=".pdf,.doc,.docx,.txt"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full
           file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700
           hover:file:bg-indigo-100 mb-4"
        />
        <button
          type="submit"
          className="bg-indigo-600 text-white px-4 py-2 rounded-xl hover:bg-indigo-700 transition"
        >
          Upload Resume
        </button>
      </form>
    </div>
  );
};

export default ResumeUpload;
