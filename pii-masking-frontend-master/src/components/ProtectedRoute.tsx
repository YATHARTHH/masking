import { type ReactNode } from "react";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children, adminOnly = false }: {children: ReactNode, adminOnly?: boolean}) => {

    const userString = sessionStorage.getItem('user') || ''

    const user: User = JSON.parse(userString)

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    if (adminOnly && !user.is_admin) {
        return <Navigate to="/user-dashboard" replace />;
    }

    return children;
};

export default ProtectedRoute