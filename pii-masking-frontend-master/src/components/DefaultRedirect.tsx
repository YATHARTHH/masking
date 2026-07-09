import getCookie from "@/utils/getCookie";
import { Navigate } from "react-router-dom";

const DefaultRedirect = () => {
    const token = getCookie('access_token');
    const userData = sessionStorage.getItem('user');

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    if (userData) {
        const user = JSON.parse(userData);
        if (user.is_admin) {
            return <Navigate to="/admin-options" replace />;
        } else {
            return <Navigate to="/user-dashboard" replace />;
        }
    }

    return <Navigate to="/login" replace />;
};

export default DefaultRedirect;