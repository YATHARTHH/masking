import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

interface ProcessedFileResult {
  filename: string;
  status: string;
  processed_filename?: string;
  download_url?: string;
  error?: string;
}

const BatchProcessingPage: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [piiCategories, setPiiCategories] = useState<string>("Email, Phone Number, SSN, Credit Card");
  const [highlightMode, setHighlightMode] = useState<string>("blur");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [results, setResults] = useState<ProcessedFileResult[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(e.target.files);
    }
  };

  const handleBatchSubmit = async () => {
    if (!selectedFiles || selectedFiles.length === 0) {
      alert("Please select at least one file to process.");
      return;
    }

    setIsProcessing(true);
    setResults([]);

    const formData = new FormData();
    for (let i = 0; i < selectedFiles.length; i++) {
      formData.append("files", selectedFiles[i]);
    }
    formData.append("pii_category", piiCategories);
    formData.append("highlight_mode", highlightMode);

    try {
      const response = await fetch("http://localhost:8000/api/v1/batch", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (data.processed_files) {
        setResults(data.processed_files);
      }
    } catch (err) {
      alert("Batch processing error: " + err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Enterprise Batch Processing Workspace</h1>
          <p className="text-slate-400 text-sm mt-1">Upload multiple documents simultaneously for automated parallel PII sanitization</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Settings Panel */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-6 h-fit">
            <h2 className="text-lg font-bold text-white">Batch Configuration</h2>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Target PII Categories (comma separated)
              </label>
              <input
                type="text"
                value={piiCategories}
                onChange={(e) => setPiiCategories(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Redaction Mode
              </label>
              <select
                value={highlightMode}
                onChange={(e) => setHighlightMode(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="blur">Soft Blur Overlay</option>
                <option value="bbox">Solid Paint Box</option>
                <option value="general">Generic [MASKED] Text</option>
                <option value="x_mask">X-Character Preservation</option>
              </select>
            </div>

            <button
              onClick={handleBatchSubmit}
              disabled={isProcessing}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-indigo-500/20"
            >
              {isProcessing ? "Processing Batch..." : "Run Batch Redaction"}
            </button>
          </div>

          {/* File Upload & Results Area */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-slate-900/80 border-2 border-dashed border-slate-800 hover:border-indigo-500/50 rounded-2xl p-8 text-center transition-all">
              <input
                type="file"
                multiple
                onChange={handleFileChange}
                className="hidden"
                id="batch-file-input"
              />
              <label htmlFor="batch-file-input" className="cursor-pointer space-y-3 block">
                <div className="text-4xl">📁</div>
                <div className="text-base font-semibold text-slate-200">
                  {selectedFiles ? `${selectedFiles.length} files selected` : "Click to select multiple files for batching"}
                </div>
                <div className="text-xs text-slate-500">Supports PDF, DOCX, CSV, PNG, JPG, MP3, MP4</div>
              </label>
            </div>

            {/* Results Grid */}
            {results.length > 0 && (
              <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
                <h3 className="text-md font-bold text-white">Batch Output Summary</h3>
                <div className="divide-y divide-slate-800">
                  {results.map((res, idx) => (
                    <div key={idx} className="py-3 flex justify-between items-center text-sm">
                      <span className="font-medium text-slate-200">{res.filename}</span>
                      {res.status === "SUCCESS" ? (
                        <a
                          href={`http://localhost:8000${res.download_url}`}
                          target="_blank"
                          rel="noreferrer"
                          className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-lg text-xs font-semibold hover:bg-emerald-500/20"
                        >
                          Download Redacted File
                        </a>
                      ) : (
                        <span className="text-rose-400 text-xs font-medium">Failed: {res.error}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default BatchProcessingPage;
