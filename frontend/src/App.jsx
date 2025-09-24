import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import SignIn from "./pages/SignIn";
import SignUp from "./pages/SignUp";
import Dashboard from "./pages/Dashboard";
import PrivateRoute from "./components/PrivateRoute";
import { AuthProvider } from "./context/AuthContext";
import ResumeUpload from "./pages/ResumeUpload";
import AnalyzeSkills from "./pages/AnalyzeSkills";
import Settings from "./pages/Settings";
import PostJob from "./pages/PostJob";

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />

          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />

          <Route
            path="/upload-resume"
            element={
              <PrivateRoute>
                <ResumeUpload />
              </PrivateRoute>
            }
          />
<Route
  path="/post-job"
  element={
    <PrivateRoute allowedRoles={["company"]}>
      <PostJob />
    </PrivateRoute>
  }
/>

<Route
  path="/analyze-skills"
  element={
    <PrivateRoute allowedRoles={["candidate"]}>
      <AnalyzeSkills />
    </PrivateRoute>
  }
/>


          <Route
            path="/settings"
            element={
              <PrivateRoute>
                <Settings />
              </PrivateRoute>
            }
          />


          <Route
            path="/"
            element={
              <div className="min-h-screen flex items-center justify-center text-center">
                <div>
                  <h1 className="text-3xl font-bold mb-4">
                    Welcome to Skill Gap Analyzer
                  </h1>
                  <Link to="/signin" className="text-blue-600 underline">
                    Sign In
                  </Link>{" "}
                  |{" "}
                  <Link to="/signup" className="text-green-600 underline">
                    Sign Up
                  </Link>
                </div>
              </div>
            }
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
