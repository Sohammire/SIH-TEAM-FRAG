import { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Eye, CheckCircle, AlertTriangle, Shield, RefreshCw, XCircle } from 'lucide-react';
import DataSourceBadge from '../components/common/DataSourceBadge';
import { predictVision } from '../api';

export default function VisionPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [selectedTyre, setSelectedTyre] = useState('TYRE_03_RRO');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setApiError(null);
    }
  };

  const handleRunInference = async () => {
    setLoading(true);
    setApiError(null);

    const formData = new FormData();
    if (selectedFile) {
      formData.append('file', selectedFile);
    }
    formData.append('tyre_id', selectedTyre);

    try {
      const res = await predictVision(formData);
      if (res.error) {
        setApiError(res.error);
      } else {
        setResult(res.data);
      }
    } catch (err) {
      setApiError(err.message || 'Vision API execution failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Computer Vision Tyre Damage Inspection</h1>
          <p className="text-xs text-slate-400 mt-1">Ultralytics YOLO Damage Detector + Image Quality Check Pipeline</p>
        </div>
        <DataSourceBadge source="model" />
      </div>

      {/* Main Grid: Upload & Result */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Image Upload & Controls */}
        <div className="card space-y-4">
          <h3 className="text-sm font-semibold text-white">Upload Inspection Image</h3>

          <div>
            <label className="text-xs text-slate-400 block mb-1">Target Tyre ID</label>
            <select
              value={selectedTyre}
              onChange={(e) => setSelectedTyre(e.target.value)}
              className="w-full bg-[var(--color-surface-700)] text-white text-xs rounded-lg px-3 py-2 border border-[var(--color-surface-600)]"
            >
              <option value="TYRE_03_RRO">TYRE_03_RRO (DUMPER_03 - Sidewall Cut)</option>
              <option value="TYRE_07_RRI">TYRE_07_RRI (DUMPER_07 - Pressure Loss)</option>
              <option value="TYRE_01_FL">TYRE_01_FL (DUMPER_01 - Clean Normal)</option>
              <option value="TYRE_05_RLI">TYRE_05_RLI (DUMPER_05 - Tread Damage)</option>
            </select>
          </div>

          <div className="border-2 border-dashed border-[var(--color-surface-600)] rounded-xl p-6 text-center bg-[var(--color-surface-800)] hover:border-blue-500/50 transition-colors">
            {previewUrl ? (
              <div className="relative inline-block mx-auto">
                <img src={previewUrl} alt="Inspection Preview" className="max-h-56 mx-auto rounded-lg object-cover mb-2 border border-[var(--color-surface-600)]" />
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2 text-slate-400">
                <Upload size={36} className="text-slate-500" />
                <p className="text-xs">Drag & drop tyre inspection image or click to browse</p>
                <span className="text-[10px] text-slate-500">Supports JPG, PNG (or click button to run synthetic test)</span>
              </div>
            )}
            <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" id="vision-file-input" />
            <label htmlFor="vision-file-input" className="mt-3 inline-block btn-secondary text-xs cursor-pointer">
              Choose File
            </label>
          </div>

          <button
            onClick={handleRunInference}
            disabled={loading}
            className="w-full py-3 rounded-lg bg-blue-600 text-white font-semibold text-xs hover:bg-blue-500 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? <RefreshCw size={14} className="animate-spin" /> : <Eye size={14} />}
            {loading ? "Running YOLO Inference Service..." : "Execute Vision Inspection Pipeline"}
          </button>
        </div>

        {/* Right Column: Inference Results */}
        <div className="card space-y-4">
          <h3 className="text-sm font-semibold text-white">YOLO Inference Result</h3>

          {/* Loading Indicator */}
          {loading && (
            <div className="flex flex-col items-center justify-center min-h-[250px] text-slate-400 gap-3">
              <RefreshCw size={28} className="animate-spin text-blue-500" />
              <p className="text-xs">Processing image through Image Quality Check & YOLO Detector...</p>
            </div>
          )}

          {/* API Error State */}
          {!loading && apiError && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 space-y-2">
              <div className="flex items-center gap-2 font-bold text-xs">
                <XCircle size={16} /> API Error
              </div>
              <p className="text-xs">{apiError}</p>
            </div>
          )}

          {/* Prediction Results */}
          {!loading && !apiError && result && (
            <div className="space-y-4">
              {/* Quality Check Alert */}
              {result.quality_warning ? (
                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 space-y-2">
                  <div className="flex items-center gap-2 font-bold text-xs">
                    <AlertTriangle size={16} /> Image Quality Check Warning
                  </div>
                  <p className="text-xs leading-relaxed">{result.warning_reason || 'Image quality check flagged potential blur, darkness, or resolution issue.'}</p>
                  <p className="text-[10px] text-slate-400">Quality check guardrail prevents unconfident YOLO detections on poor-quality images.</p>
                </div>
              ) : (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-2 text-xs">
                  <CheckCircle size={16} /> Image Quality Check Passed (Valid Resolution & Clarity)
                </div>
              )}

              {/* Main Metadata */}
              <div className="grid grid-cols-2 gap-3 p-4 rounded-xl bg-[var(--color-surface-700)] border border-[var(--color-surface-600)]">
                <div>
                  <span className="text-[10px] text-slate-400 block">Image ID</span>
                  <span className="text-xs font-mono font-bold text-white">{result.image_id || 'IMG_01'}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Target Tyre ID</span>
                  <span className="text-xs font-bold text-white">{result.tyre_id || selectedTyre}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Damage Status</span>
                  <span className={`text-xs font-bold ${result.damage_present ? 'text-red-400' : 'text-emerald-400'}`}>
                    {result.damage_present ? 'DAMAGE DETECTED' : 'NORMAL (No Damage)'}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Model Version</span>
                  <span className="text-xs font-mono text-blue-400">{result.model_version || 'yolov8n-tire-damage-v1.0'}</span>
                </div>
              </div>

              {/* Detections List */}
              {result.damage_present && result.detections && result.detections.length > 0 ? (
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-white block">Detected Bounding Boxes ({result.detections.length})</span>
                  {result.detections.map((det, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-[var(--color-surface-700)] border border-[var(--color-surface-600)] flex items-center justify-between text-xs">
                      <div>
                        <span className="font-bold text-white uppercase tracking-wider">{det.class}</span>
                        <span className="text-[10px] text-slate-400 block mt-0.5 font-mono">
                          BBox [x1, y1, x2, y2]: {JSON.stringify(det.bbox)}
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-[10px] text-slate-400 block">Confidence</span>
                        <span className="font-bold text-blue-400">{Math.round(det.confidence * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : !result.quality_warning ? (
                <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-center text-xs text-emerald-300">
                  <CheckCircle size={24} className="mx-auto mb-1 text-emerald-400" />
                  <p className="font-semibold">Normal Clean Tyre</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">No damage defects detected by YOLO model.</p>
                </div>
              ) : null}
            </div>
          )}

          {/* Empty Initial State */}
          {!loading && !apiError && !result && (
            <div className="flex flex-col items-center justify-center min-h-[250px] text-slate-500 text-xs">
              <Shield size={36} className="mb-2 text-slate-600" />
              <p>Upload an image and click "Execute Vision Inspection Pipeline"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
