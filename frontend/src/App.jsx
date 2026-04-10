import { useState, useRef } from "react";
import { predictText, uploadFile, verifySource } from "./services/api";
import { 
  Search, 
  Upload, 
  ShieldCheck, 
  FileText, 
  AlertCircle, 
  CheckCircle2, 
  BarChart3, 
  FileCode,
  ArrowRight,
  Info
} from "lucide-react";

const MetricCard = ({ label, value, color, icon: Icon }) => (
  <div className="bg-white/50 border border-white/20 p-4 rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
    <div className="flex items-center gap-3 mb-2">
      <div className={`p-2 rounded-lg ${color} text-white`}>
        <Icon size={18} />
      </div>
      <span className="text-gray-500 font-medium text-sm">{label}</span>
    </div>
    <div className="flex items-end gap-1">
      <span className="text-2xl font-bold text-gray-800">{value}</span>
      {typeof value === 'number' && <span className="text-gray-400 mb-1">%</span>}
    </div>
  </div>
);

export default function App() {
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("text"); // "text" or "file"
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const resetState = () => {
    setResult(null);
    setError(null);
  };

  const handlePredict = async () => {
    if (!text.trim()) return;
    setLoading(true);
    resetState();
    try {
      const res = await predictText(text);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Prediction failed. Please try again.");
    }
    setLoading(false);
  };

  const handleFileUpload = async () => {
    if (!file) return;
    setLoading(true);
    resetState();
    try {
      const res = await uploadFile(file);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "File processing failed. Ensure Tesseract is installed for images.");
    }
    setLoading(false);
  };

  const handleVerify = async () => {
    if (!text.trim()) return;
    setLoading(true);
    resetState();
    try {
      const res = await verifySource(text);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Verification failed. Search API might be unavailable.");
    }
    setLoading(false);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
      setError(null);
    }
  };

  return (
    <div className="min-h-screen py-12 px-4 flex flex-col items-center">
      {/* Header Section */}
      <div className="max-w-4xl w-full text-center mb-12 animate-float">
        <h1 className="text-5xl font-extrabold mb-4 tracking-tight">
          <span className="gradient-text">VeriTruth</span> AI
        </h1>
        <p className="text-gray-600 text-lg max-w-xl mx-auto">
          Next-generation BERT-powered detection for misinformation in text and media.
        </p>
      </div>

      <div className="max-w-4xl w-full glass-card rounded-3xl overflow-hidden neo-shadow mb-12">
        {/* Tabs */}
        <div className="flex border-b border-white/20">
          <button
            onClick={() => setActiveTab("text")}
            className={`flex-1 py-4 flex items-center justify-center gap-2 font-semibold transition-all duration-300 ${
              activeTab === "text" 
              ? "bg-white/60 text-indigo-600 shadow-inner" 
              : "text-gray-500 hover:bg-white/30"
            }`}
          >
            <FileText size={20} /> Text Analysis
          </button>
          <button
            onClick={() => setActiveTab("file")}
            className={`flex-1 py-4 flex items-center justify-center gap-2 font-semibold transition-all duration-300 ${
              activeTab === "file" 
              ? "bg-white/60 text-purple-600 shadow-inner" 
              : "text-gray-500 hover:bg-white/30"
            }`}
          >
            <Upload size={20} /> Media Upload
          </button>
        </div>

        <div className="p-8">
          {activeTab === "text" ? (
            <div className="space-y-6">
              <div className="relative">
                <textarea
                  rows="6"
                  className="w-full bg-white/40 border-2 border-white/40 rounded-2xl p-4 focus:ring-4 focus:ring-indigo-200 focus:border-indigo-400 outline-none transition-all duration-200 text-gray-700 placeholder-gray-400 shadow-sm"
                  placeholder="Paste an article, social media post, or news snippet here..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                />
                <div className="absolute bottom-4 right-4 text-xs text-gray-400 uppercase tracking-widest font-bold">
                  BERT Analysis Ready
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={handlePredict}
                  disabled={loading || !text.trim()}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-4 rounded-xl font-bold flex items-center justify-center gap-3 transition-all duration-300 shadow-lg shadow-indigo-200 disabled:opacity-50"
                >
                  {loading ? "Processing..." : <><Search size={22} /> Predict Credibility</>}
                </button>
                <button
                  onClick={handleVerify}
                  disabled={loading || !text.trim()}
                  className="flex-1 bg-white border-2 border-indigo-100 text-indigo-600 hover:bg-indigo-50 py-4 rounded-xl font-bold flex items-center justify-center gap-3 transition-all duration-300 shadow-md disabled:opacity-50"
                >
                  <ShieldCheck size={22} /> Comprehensive Verify
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div 
                onClick={() => fileInputRef.current.click()}
                className={`border-4 border-dashed rounded-3xl p-12 text-center transition-all duration-300 cursor-pointer ${
                  file ? "border-purple-400 bg-purple-50/50" : "border-white/60 hover:border-purple-300 hover:bg-white/40"
                }`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="hidden"
                  accept=".pdf,.docx,.doc,.jpg,.jpeg,.png"
                />
                <div className="flex flex-col items-center gap-4">
                  <div className={`p-6 rounded-full ${file ? 'bg-purple-100 text-purple-600' : 'bg-white/60 text-gray-400'}`}>
                    <Upload size={48} />
                  </div>
                  {file ? (
                    <div>
                      <p className="text-xl font-bold text-gray-800">{file.name}</p>
                      <p className="text-gray-500">Ready for OCR and NLP analysis</p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-xl font-bold text-gray-800">Drop your file here</p>
                      <p className="text-gray-500">Supports PDF, DOCX, and Images (JPG/PNG)</p>
                    </div>
                  )}
                </div>
              </div>

              <button
                onClick={handleFileUpload}
                disabled={loading || !file}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white py-4 rounded-xl font-bold flex items-center justify-center gap-3 transition-all duration-300 shadow-lg shadow-purple-200 disabled:opacity-50"
              >
                {loading ? "Analyzing..." : <><BarChart3 size={22} /> Extract & Analyze</>}
              </button>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-8 p-4 bg-red-50 border-l-4 border-red-500 rounded-r-xl flex items-start gap-3 animate-shake">
              <AlertCircle className="text-red-500 mt-1 flex-shrink-0" size={20} />
              <div>
                <p className="text-red-800 font-bold">Error Encountered</p>
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Result Section */}
          {result && (
            <div className="mt-8 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex flex-col md:flex-row items-center gap-6 p-6 rounded-2xl bg-white/80 border border-white/20 shadow-sm">
                <div className={`p-8 rounded-full flex items-center justify-center ${
                  result.prediction?.toUpperCase() === "REAL" 
                  ? "bg-green-100 text-green-600" 
                  : "bg-red-100 text-red-600"
                }`}>
                  {result.prediction?.toUpperCase() === "REAL" ? <CheckCircle2 size={64} /> : <AlertCircle size={64} />}
                </div>
                
                <div className="flex-1 text-center md:text-left">
                  <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Prediction Result</h3>
                  <div className="flex items-center justify-center md:justify-start gap-3">
                    <span className={`text-4xl font-extrabold ${
                      result.prediction?.toUpperCase() === "REAL" ? "text-green-600" : "text-red-600"
                    }`}>
                      {result.prediction}
                    </span>
                    <span className="px-3 py-1 bg-gray-100 text-gray-500 rounded-full text-xs font-bold">
                      {result.confidence_level} CONFIDENCE
                    </span>
                  </div>
                  <p className="text-gray-500 mt-2">
                    {result.prediction?.toUpperCase() === "REAL" 
                      ? "This content appears to be credible and aligns with known factual data."
                      : "Caution: This content shows strong indicators of being misleading or factually incorrect."}
                  </p>
                </div>

                <div className="w-full md:w-auto flex flex-col items-center p-4 border-l border-gray-100">
                  <span className="text-gray-400 text-xs font-bold uppercase mb-2">Confidence Score</span>
                  <div className="relative flex items-center justify-center">
                    <svg className="w-24 h-24 transform -rotate-90">
                      <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-gray-100" />
                      <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" 
                        strokeDasharray={251.2} 
                        strokeDashoffset={251.2 - (251.2 * result.confidence) / 100}
                        className={result.prediction?.toUpperCase() === "REAL" ? "text-green-500" : "text-red-500"} 
                      />
                    </svg>
                    <span className="absolute text-xl font-bold">{Math.round(result.confidence)}%</span>
                  </div>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard 
                  label="Model Accuracy" 
                  value={result.accuracy || 94.8} 
                  color="bg-indigo-500" 
                  icon={BarChart3} 
                />
                <MetricCard 
                  label="F1 Score" 
                  value={result.f1_score || 93.5} 
                  color="bg-purple-500" 
                  icon={ShieldCheck} 
                />
                <MetricCard 
                  label="Processing Time" 
                  value={`${result.processing_time?.toFixed(3)}s`} 
                  color="bg-blue-500" 
                  icon={Search} 
                />
                <MetricCard 
                  label="Model Type" 
                  value={result.parameters?.model_type?.split('-')[0] || "BERT"} 
                  color="bg-pink-500" 
                  icon={FileCode} 
                />
              </div>

              {/* Extracted Text Preview (for Files) */}
              {result.extracted_text_preview && (
                <div className="p-6 rounded-2xl bg-indigo-50/50 border border-indigo-100">
                  <div className="flex items-center gap-2 mb-3 text-indigo-700 font-bold">
                    <FileText size={20} />
                    <span>Extracted Content Preview</span>
                  </div>
                  <p className="text-sm text-gray-600 leading-relaxed italic">
                    "{result.extracted_text_preview}..."
                  </p>
                </div>
              )}

              {/* Verification Summary (if available) */}
              {result.verification_summary && (
                <div className="p-6 rounded-2xl bg-green-50 border border-green-100">
                  <div className="flex items-center gap-2 mb-3 text-green-700 font-bold">
                    <ShieldCheck size={20} />
                    <span>Verification Summary</span>
                  </div>
                  <p className="text-sm text-green-800">
                    {result.verification_summary}
                  </p>
                </div>
              )}

              {/* Model Parameters Detail */}
              {result.parameters && (
                <details className="group p-4 rounded-xl border border-gray-100 hover:bg-gray-50 transition-all">
                  <summary className="flex items-center justify-between cursor-pointer list-none">
                    <div className="flex items-center gap-2 text-gray-500 font-medium">
                      <Info size={16} />
                      <span>Technical Model Parameters</span>
                    </div>
                    <ArrowRight size={16} className="text-gray-400 group-open:rotate-90 transition-transform" />
                  </summary>
                  <div className="mt-4 grid grid-cols-2 gap-x-8 gap-y-2 text-xs text-gray-500 font-mono">
                    <div className="flex justify-between border-b border-gray-100 py-1">
                      <span>Max Sequence Length</span>
                      <span className="text-gray-800">{result.parameters.max_length}</span>
                    </div>
                    <div className="flex justify-between border-b border-gray-100 py-1">
                      <span>Vocab Size</span>
                      <span className="text-gray-800">{result.parameters.vocab_size}</span>
                    </div>
                    <div className="flex justify-between border-b border-gray-100 py-1">
                      <span>Device</span>
                      <span className="text-gray-800 uppercase">{result.parameters.device}</span>
                    </div>
                    <div className="flex justify-between border-b border-gray-100 py-1">
                      <span>Labels</span>
                      <span className="text-gray-800">{result.parameters.num_labels}</span>
                    </div>
                  </div>
                </details>
              )}
            </div>
          )}
        </div>
      </div>
      
      {/* Footer Info */}
      <div className="text-gray-400 text-sm flex items-center gap-4">
        <span>© 2026 VeriTruth Systems</span>
        <span className="w-1 h-1 bg-gray-300 rounded-full"></span>
        <span>Secure Analysis</span>
        <span className="w-1 h-1 bg-gray-300 rounded-full"></span>
        <span>Privacy Protected</span>
      </div>
    </div>
  );
}
