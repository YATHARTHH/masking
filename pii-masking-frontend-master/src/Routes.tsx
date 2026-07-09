import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
// import ProtectedRoute from '@/components/ProtectedRoute';
import Main from '@/pages/main/Page';
// import DefaultRedirect from '@/components/DefaultRedirect';

/* ------------------------- mention all routes here ------------------------ */

export default function AppRoutes() {

    return (
        <Router>
            <Routes>
                {/* Public Routes */}
                {/* <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} /> */}


                <Route
                    path="/"
                    element={
                        // <ProtectedRoute>
                            <Main />
                        // </ProtectedRoute>
                    }
                />

                {/* <Route path="/admin" element={<ProtectedRoute adminOnly={true}><AdminMain /></ProtectedRoute>} /> */}


                {/* Default Route - Redirect based on authentication */}
                {/* <Route
                    path="/"
                    element={<DefaultRedirect />}
                /> */}

                {/* Catch all other routes */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Router>
    );
}