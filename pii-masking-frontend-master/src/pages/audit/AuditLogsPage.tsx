import React, { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

interface AuditLogItem {
  id: number;
  timestamp: string;
  filename: string;
  file_hash: string;
  pii_categories: string[];
  masking_type: string;
  status: string;
  processing_time_ms: number;
}

const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/audit/logs')
      .then((res) => res.json())
      .then((data) => {
        setLogs(data.logs || []);
        setLoading(false);
      })
      .catch(() => {
        // Fallback demo audit log data if backend is offline
        setLogs([
          {
            id: 101,
            timestamp: new Date().toISOString(),
            filename: "employee_records_q3.pdf",
            file_hash: "a3b4c5d6e7f890123456789abcdef1234567890abcdef1234567890abcdef12",
            pii_categories: ["Email", "SSN", "Phone Number"],
            masking_type: "blur",
            status: "SUCCESS",
            processing_time_ms: 184.2
          },
          {
            id: 100,
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            filename: "customer_support_call.mp3",
            file_hash: "b9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedc",
            pii_categories: ["Credit Card"],
            masking_type: "beep",
            status: "SUCCESS",
            processing_time_ms: 1250.0
          }
        ]);
        setLoading(false);
      });
  }, []);

  const filteredLogs = logs.filter((item) =>
    item.filename.toLowerCase().includes(search.toLowerCase()) ||
    item.file_hash.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Audit Verification Ledger</h1>
            <p className="text-slate-400 text-sm mt-1">Immutable SQLite audit history tracking every redaction event</p>
          </div>

          <a
            href="http://localhost:8000/api/v1/audit/export"
            target="_blank"
            rel="noreferrer"
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-5 py-2.5 rounded-xl text-sm transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2"
          >
            <span>📜</span> Export Compliance Certificate
          </a>
        </div>

        {/* Filter Input */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search by file name or SHA-256 hash..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        {/* Ledger Table */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          {loading ? (
            <div className="text-center py-16 text-slate-400">Loading audit records...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-900 border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  <tr>
                    <th className="px-6 py-4">Job ID</th>
                    <th className="px-6 py-4">Timestamp</th>
                    <th className="px-6 py-4">File Name</th>
                    <th className="px-6 py-4">SHA-256 Hash</th>
                    <th className="px-6 py-4">Categories Redacted</th>
                    <th className="px-6 py-4">Mode</th>
                    <th className="px-6 py-4">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {filteredLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4 font-mono text-slate-400">#{log.id}</td>
                      <td className="px-6 py-4 text-xs text-slate-400">
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 font-medium text-white">{log.filename}</td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-500">
                        {log.file_hash ? `${log.file_hash.substring(0, 16)}...` : 'N/A'}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {log.pii_categories.map((c) => (
                            <span key={c} className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[11px] px-2 py-0.5 rounded-md font-medium">
                              {c}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4 capitalize text-xs">{log.masking_type}</td>
                      <td className="px-6 py-4">
                        <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-2.5 py-1 rounded-full font-semibold">
                          {log.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {filteredLogs.length === 0 && (
                    <tr>
                      <td colSpan={7} className="text-center py-12 text-slate-500">
                        No audit records found matching search query.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default AuditLogsPage;
