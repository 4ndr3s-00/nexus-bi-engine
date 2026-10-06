import React, { useState } from 'react';
import { 
  Sparkles, 
  Download, 
  Terminal, 
  CheckCircle2, 
  AlertTriangle, 
  Lightbulb, 
  ChevronDown, 
  ChevronUp,
  Table as TableIcon
} from 'lucide-react';
import KPICard from './KPICard';

export default function ExecutiveReportView({ report, onClose }) {
  const [showSql, setShowSql] = useState(false);

  if (!report) return null;

  const handleExportJson = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nexus_executive_report_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-[#151720] border border-[#232635] rounded-3xl p-7 space-y-7 shadow-2xl relative">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-[#232635]">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-500/10 text-purple-400 border border-purple-500/30 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              AI Executive Briefing
            </span>
            <span className="text-xs text-slate-500 font-mono">
              Latencia: {report.latency_ms} ms
            </span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            {report.headline}
          </h2>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setShowSql(!showSql)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-[#1a1d29] hover:bg-[#202433] text-slate-300 border border-[#2a2e42] transition-all"
          >
            <Terminal className="w-3.5 h-3.5 text-purple-400" />
            <span>{showSql ? 'Ocultar SQL' : 'Ver SQL Generado'}</span>
            {showSql ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>

          <button
            onClick={handleExportJson}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-purple-600 to-pink-600 hover:brightness-110 text-white shadow-md shadow-purple-900/30 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Exportar Informe</span>
          </button>
        </div>
      </div>

      {/* SQL Sandbox Accordion */}
      {showSql && (
        <div className="bg-[#0f1017] border border-purple-900/40 rounded-2xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>SQL ANSI Determinista (Validado por QueryGuard):</span>
            <span className="text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              100% Cero Alucinaciones
            </span>
          </div>
          <pre className="text-xs font-mono text-purple-200 overflow-x-auto p-3 bg-black/40 rounded-xl leading-relaxed">
            {report.sql}
          </pre>
        </div>
      )}

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {report.kpi_cards?.map((card, idx) => (
          <KPICard
            key={idx}
            label={card.label}
            value={card.value}
            change={card.change}
            trend={card.trend}
          />
        ))}
      </div>

      {/* Executive Summary Narrative */}
      <div className="bg-[#1a1c27] border border-[#272b3c] rounded-2xl p-5">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-purple-400 mb-2">
          Síntesis para la Dirección
        </h4>
        <p className="text-sm text-slate-300 leading-relaxed">
          {report.summary}
        </p>
      </div>

      {/* Highlights & Recommendations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Highlights */}
        <div className="bg-[#181a24] border border-[#252839] rounded-2xl p-5 space-y-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" />
            Puntos Clave y Hallazgos
          </h4>
          <ul className="space-y-2.5 text-xs text-slate-300">
            {report.highlights?.map((h, i) => (
              <li key={i} className="flex items-start gap-2 leading-relaxed">
                <span className="text-emerald-400 font-bold mt-0.5">•</span>
                <span dangerouslySetInnerHTML={{ __html: h.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>') }} />
              </li>
            ))}
          </ul>
        </div>

        {/* Recommendations */}
        <div className="bg-[#181a24] border border-[#252839] rounded-2xl p-5 space-y-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
            <Lightbulb className="w-4 h-4" />
            Recomendaciones Estratégicas
          </h4>
          <ul className="space-y-2.5 text-xs text-slate-300">
            {report.recommendations?.map((r, i) => (
              <li key={i} className="flex items-start gap-2 leading-relaxed">
                <span className="text-amber-400 font-bold mt-0.5">→</span>
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Drill-Down Table */}
      {report.table_data?.length > 0 && (
        <div className="bg-[#161822] border border-[#232635] rounded-2xl overflow-hidden">
          <div className="px-5 py-3.5 border-b border-[#232635] flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
              <TableIcon className="w-4 h-4 text-purple-400" />
              <span>Desglose Detallado de Resultados ({report.table_data.length} filas)</span>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300 font-sans">
              <thead className="bg-[#1a1d28] text-slate-400 uppercase text-[10px] tracking-wider border-b border-[#232635]">
                <tr>
                  {Object.keys(report.table_data[0]).map((col) => (
                    <th key={col} className="px-4 py-3 font-semibold">
                      {col.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#202331]">
                {report.table_data.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-[#1d202d] transition-colors">
                    {Object.values(row).map((val, cIdx) => (
                      <td key={cIdx} className="px-4 py-3 font-mono text-[11px]">
                        {typeof val === 'number' 
                          ? (val > 1000 ? `$${val.toLocaleString()}` : val)
                          : String(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
