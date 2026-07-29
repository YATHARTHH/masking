import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

interface DetectionMatches {
  [category: string]: string[];
}

const HITLPreviewWorkbench: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [piiCategories, setPiiCategories] = useState<string>("Email, Phone Number, SSN, Credit Card, IP Address");
  const [loading, setLoading] = useState<boolean>(false);
  const [previewResult, setPreviewResult] = useState<{
    filename: string;
    total_matches: number;
    detected_items: DetectionMatches;
    recommendation: string;
  } | null>(null);

  const handleInspect = async () => {
    if (!file) {
      alert("Please select a document or image to inspect.");
      return;
    }

    setLoading(true);
    setPreviewResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("pii_category", piiCategories);

    try {
      const response = await fetch("http://localhost:8000/api/v1/preview", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setPreviewResult(data);
    } catch (err) {
      alert("HITL Inspection error: " + err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Human-in-the-Loop (HITL) Review Workbench</h1>
          <p className="text-slate-400 text-sm mt-1">Pre-inspection review queue for compliance officers to verify detected PII entities before destructive masking</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Inspection Controls */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-6">
            <h2 className="text-lg font-bold text-white">Target Document Inspection</h2>

            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl">
              <input
                type="file"
                onChange={(e) => e.target.files && setFile(e.target.files[0])}
                className="text-sm text-slate-300"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Categories to Scan
              </label>
              <input
                type="text"
                value={piiCategories}
                onChange={(e) => setPiiCategories(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <button
              onClick={handleInspect}
              disabled={loading || !file}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-indigo-500/20"
            >
              {loading ? "Scanning for PII Entities..." : "Run Inspection Pre-Check"}
            </button>
          </div>

          {/* Inspection Results */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl">
            <h2 className="text-lg font-bold text-white mb-4">Inspection Findings</h2>

            {loading ? (
              <div className="text-center py-16 text-slate-400">Analyzing document structure...</div>
            ) : previewResult ? (
              <div className="space-y-6">
                <div className="flex justify-between items-center bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div>
                    <div className="text-xs text-slate-500">Document</div>
                    <div className="font-semibold text-slate-200">{previewResult.filename}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-slate-500">Entities Detected</div>
                    <div className="text-xl font-bold text-indigo-400">{previewResult.total_matches}</div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Entity Verification List</div>
                  {Object.keys(previewResult.detected_items).length === 0 ? (
                    <div className="text-sm text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-xl">
                      ✓ Zero sensitive entities detected. Safe for publication without masking.
                    </div>
                  ) : (
                    Object.entries(previewResult.detected_items).map(([cat, items]) => (
                      <div key={cat} className="bg-slate-950 border border-slate-800 p-3 rounded-xl">
                        <div className="text-xs font-bold text-indigo-400 mb-1">{cat}</div>
                        <div className="flex flex-wrap gap-2">
                          {items.map((item, i) => (
                            <span key={i} className="bg-slate-900 border border-slate-700 text-slate-200 text-xs px-2.5 py-1 rounded-md font-mono">
                              {item}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-16 text-slate-500 text-sm">
                Select a document and run inspection to verify entity locations before applying redaction rules.
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default HITLPreviewWorkbench;
