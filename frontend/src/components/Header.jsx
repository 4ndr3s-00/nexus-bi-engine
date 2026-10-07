import React from 'react';
import { Search, Sparkles, Clock, RefreshCw } from 'lucide-react';

export default function Header({ 
  query, 
  setQuery, 
  onRunQuery, 
  isLoading, 
  latencyMs, 
  onRefresh,
  onSelectSuggestion
}) {
  const suggestions = [
    "¿Cuál es el tiempo de espera promedio en Triage en los hospitales 24 horas?",
    "Ocupación de camas UCI por sede hospitalaria",
    "¿Qué EPS tiene mayor valor de glosas objetadas?",
    "Oportunidad de citas en cardiología",
    "Cuáles son los diagnósticos CIE-10 más frecuentes en urgencias"
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onRunQuery(query);
    }
  };

  return (
    <header className="border-b border-[#222533] px-8 py-4 bg-[#0d0e12]/80 backdrop-blur-md sticky top-0 z-20 space-y-3">
      <div className="flex items-center justify-between gap-6">
        {/* Search Bar with AI Button */}
        <form onSubmit={handleSubmit} className="flex-1 max-w-3xl relative">
          <div className="relative flex items-center">
            <Search className="w-4 h-4 text-slate-400 absolute left-4 pointer-events-none" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Consulta a la IA: 'Tiempo de espera en Triage en hospitales 24h', 'Ocupación UCI', 'Glosas por EPS'..."
              className="w-full bg-[#151720] border border-[#232635] text-sm text-slate-100 placeholder-slate-500 rounded-2xl pl-11 pr-32 py-2.5 focus:outline-none focus:border-purple-500/60 focus:ring-1 focus:ring-purple-500/50 transition-all font-sans"
            />
            <button 
              type="submit"
              disabled={isLoading || !query.trim()}
              className="absolute right-1.5 px-4 py-1.5 bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 hover:brightness-110 active:scale-95 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-purple-900/30 transition-all disabled:opacity-50"
            >
              <Sparkles className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              <span>{isLoading ? 'Analizando...' : 'AI Clinica'}</span>
            </button>
          </div>
        </form>

        {/* Actions & Metrics */}
        <div className="flex items-center gap-3 shrink-0">
          <button 
            onClick={onRefresh}
            title="Refrescar métricas clínicas"
            className="p-2.5 rounded-xl border border-[#232635] bg-[#151720] text-slate-300 hover:text-white hover:bg-[#1a1d29] transition-all"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <div className="h-6 w-px bg-[#232635]"></div>
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#151720] border border-[#232635] text-xs font-mono text-purple-300">
            <Clock className="w-3.5 h-3.5 text-purple-400" />
            <span>Respuesta: {latencyMs ? `${latencyMs}ms` : '32ms'}</span>
          </div>
        </div>
      </div>

      {/* Suggestion Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs no-scrollbar">
        <span className="text-slate-500 font-medium shrink-0">Preguntas sugeridas:</span>
        {suggestions.map((s, idx) => (
          <button
            key={idx}
            onClick={() => onSelectSuggestion ? onSelectSuggestion(s) : onRunQuery(s)}
            className="px-2.5 py-1 rounded-lg bg-[#151720] hover:bg-[#1e212e] text-slate-300 hover:text-white border border-[#232635] shrink-0 transition-all text-[11px]"
          >
            {s}
          </button>
        ))}
      </div>
    </header>
  );
}
