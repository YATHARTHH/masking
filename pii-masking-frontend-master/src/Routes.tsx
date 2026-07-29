import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Main from '@/pages/main/Page';
import AnalyticsDashboard from '@/pages/analytics/AnalyticsDashboard';
import AuditLogsPage from '@/pages/audit/AuditLogsPage';
import BatchProcessingPage from '@/pages/batch/BatchProcessingPage';
import HITLPreviewWorkbench from '@/pages/preview/HITLPreviewWorkbench';

export default function AppRoutes() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Main />} />
                <Route path="/analytics" element={<AnalyticsDashboard />} />
                <Route path="/audit" element={<AuditLogsPage />} />
                <Route path="/batch" element={<BatchProcessingPage />} />
                <Route path="/preview" element={<HITLPreviewWorkbench />} />

                {/* Catch all other routes */}
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Router>
    );
}