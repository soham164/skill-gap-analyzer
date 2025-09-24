// src/components/PrivateRoute.jsx
import { useAuth } from "../context/AuthContext";
import { Navigate } from "react-router-dom";

const PrivateRoute = ({ children }) => {
  const { user, token } = useAuth();

  // If either user or token exists, consider authenticated
  const isAuthenticated = user && token;

  return isAuthenticated ? children : <Navigate to="/signin" />;
};

export default PrivateRoute;
