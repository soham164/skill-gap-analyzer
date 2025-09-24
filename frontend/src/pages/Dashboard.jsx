import React, { useState } from "react";
import { BarChart3, Brain, Target, Settings, Users, Briefcase } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  // fallback if no user found
  const userName = user?.name || "Guest";

  const handleAnalyzeSkills = () => {
    navigate("/analyze-skills");
  };

  const handlePostJob = () => {
    navigate("/post-job");
  };

  const handleNavigation = (page) => {
    navigate(`/${page}`);
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-lg hidden md:block border-r border-gray-200">
        <div className="p-6 text-xl font-bold border-b border-gray-200 bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-tr-lg">
          SkillGap Analyzer
        </div>
        <nav className="p-4 space-y-2">
          <button
            onClick={() => handleNavigation("dashboard")}
            className="flex items-center px-4 py-3 text-indigo-600 bg-indigo-50 rounded-lg font-medium border border-indigo-200 w-full text-left"
          >
            <BarChart3 className="w-5 h-5 mr-3" />
            Dashboard
          </button>

          {/* Both options visible for all users */}
          <button
            onClick={() => handleNavigation("analyze-skills")}
            className="flex items-center px-4 py-3 text-gray-700 hover:text-indigo-600 hover:bg-gray-50 rounded-lg transition-all duration-200 w-full text-left"
          >
            <Brain className="w-5 h-5 mr-3" />
            Analyze Skills
          </button>

          <button
            onClick={() => handleNavigation("post-job")}
            className="flex items-center px-4 py-3 text-gray-700 hover:text-indigo-600 hover:bg-gray-50 rounded-lg transition-all duration-200 w-full text-left"
          >
            <Briefcase className="w-5 h-5 mr-3" />
            Post Job
          </button>

          <button
            onClick={() => handleNavigation("settings")}
            className="flex items-center px-4 py-3 text-gray-700 hover:text-indigo-600 hover:bg-gray-50 rounded-lg transition-all duration-200 w-full text-left"
          >
            <Settings className="w-5 h-5 mr-3" />
            Settings
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-md px-6 py-4 flex justify-between items-center border-b border-gray-200">
          <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
          <div className="flex items-center space-x-4">
            <div className="text-gray-700">
              Welcome, <span className="font-medium text-indigo-600">{userName}!</span>
            </div>
            <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
              <Users className="w-5 h-5 text-indigo-600" />
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="p-6 space-y-6 overflow-y-auto flex items-center justify-center">
          <div className="max-w-4xl w-full space-y-8">
            <div className="grid grid-cols-1 gap-6">
              <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
                <div className="flex items-center mb-6">
                  <div className="bg-indigo-100 rounded-lg p-3 mr-4">
                    <BarChart3 className="w-6 h-6 text-indigo-600" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Welcome to SkillGap Analyzer
                  </h2>
                </div>

                <p className="text-gray-600 mb-8 text-lg leading-relaxed">
                  Get insights into your recent activity, track skill analysis progress, and monitor
                  alignment results. Use the Analyze Skills section to discover gaps and strengthen
                  your profile for better job opportunities.
                </p>

                {/* Quick Actions */}
                <div className="flex justify-center space-x-6">
                  <button
                    onClick={handleAnalyzeSkills}
                    className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white px-8 py-4 rounded-xl font-semibold hover:from-indigo-700 hover:to-blue-700 transition-all duration-300 shadow-lg hover:shadow-xl flex items-center justify-center"
                  >
                    <Target className="w-5 h-5 mr-2" />
                    Start Skill Analysis
                  </button>

                  <button
                    onClick={handlePostJob}
                    className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-4 rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 transition-all duration-300 shadow-lg hover:shadow-xl flex items-center justify-center"
                  >
                    <Briefcase className="w-5 h-5 mr-2" />
                    Post Job
                  </button>
                </div>

              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
