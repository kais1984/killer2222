import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const ADMIN_EMAILS = [
  "admin@rimanfashion.com",
  "kaistauiti22@gmail.com", // Your admin email
];

export const ProtectedRoute = ({ children, requireAdmin = false }: { children: React.ReactNode, requireAdmin?: boolean }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold"></div>
      </div>
    );
  }

  const isAuthenticated = !!user;

  if (!isAuthenticated) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  if (requireAdmin && user?.email && !ADMIN_EMAILS.includes(user.email)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};
