import { useState, useRef } from "react";
import { Upload, RefreshCw, Fish } from "lucide-react";

const FISH_TR = {
  "Gilt-Head Bream": "Çipura",
  "Sea Bass": "Levrek",
  "Trout": "Alabalık",
  "Black Sea Sprat": "Karadeniz Çaça Balığı",
  "Hourse Mackerel": "İstavrit",
  "Red Mullet": "Tekir",
  "Red Sea Bream": "Mercan Balığı",
  "Shrimp": "Karides",
  "Striped Red Mullet": "Barbun",
};

export default function FishClassifier() {
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleFile = (f) => {
    if (!f?.type.startsWith("image/")) return;
    setFile(f);
    setResult(null);
    setError(null);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(f);
  };

  const classify = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch("http://127.0.0.1:8000/predict", { method: "POST", body: form });
      if (!res.ok) throw new Error(`Sunucu hatası: ${res.status}`);
      const data = await res.json();
      if (!data.success) throw new Error("Tahmin yapılamadı.");
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setPreview(null); setFile(null); setResult(null); setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-sm bg-gray-900 rounded-2xl border border-gray-800 p-6 space-y-4">

        {/* Başlık */}
        <div className="flex items-center gap-2">
          <Fish size={18} className="text-cyan-400" />
          <h1 className="text-white font-semibold text-base">Balık Türü Tanıma</h1>
        </div>

        {/* Upload alanı */}
        <div
          onClick={() => !preview && inputRef.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
          className={`relative rounded-xl border-2 border-dashed border-gray-700 overflow-hidden flex items-center justify-center cursor-pointer transition-colors hover:border-cyan-600 ${preview ? "h-48" : "h-36"}`}
        >
          {preview ? (
            <img src={preview} alt="önizleme" className="w-full h-full object-cover" />
          ) : (
            <div className="text-center space-y-2">
              <Upload size={22} className="mx-auto text-gray-500" />
              <p className="text-sm text-gray-500">Görsel seç veya sürükle</p>
            </div>
          )}
        </div>
        <input ref={inputRef} type="file" accept="image/*" className="hidden"
          onChange={(e) => handleFile(e.target.files[0])} />

        {/* Hata */}
        {error && <p className="text-red-400 text-sm">{error}</p>}

        {/* Sonuç */}
        {result && (
          <div className="bg-gray-800 rounded-xl p-4 space-y-3">
            <div>
              <p className="text-2xl font-bold text-white">{FISH_TR[result.prediction] ?? result.prediction}</p>
              <p className="text-sm text-gray-400">{result.prediction}</p>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-gray-400">
                <span>Güven</span>
                <span className="text-cyan-400 font-medium">{result.confidence.toFixed(1)}%</span>
              </div>
              <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-cyan-500 rounded-full transition-all duration-700"
                  style={{ width: `${result.confidence}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Butonlar */}
        <div className="flex gap-2">
          <button
            onClick={classify}
            disabled={!file || loading}
            className="flex-1 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium py-2.5 rounded-lg transition-colors"
          >
            {loading ? "Analiz ediliyor..." : "Türü belirle"}
          </button>
          {(preview || result) && (
            <button onClick={reset} className="px-3 py-2.5 border border-gray-700 hover:border-gray-600 text-gray-400 rounded-lg transition-colors">
              <RefreshCw size={15} />
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
