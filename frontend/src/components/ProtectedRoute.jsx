import { Navigate } from "react-router-dom";
import { useAuth } from "../state/AuthContext.jsx";

export default function ProtectedRoute({ children }) {
  const { token } = useAuth();
  
  //Redirect unauthenticated users to login and replace history
  //so they can't navigate "back" int oa protected page.
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
