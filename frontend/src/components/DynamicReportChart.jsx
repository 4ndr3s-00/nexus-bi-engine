import React from 'react';
import { 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  CartesianGrid, 
  Cell 
} from 'recharts';
import { Sparkles, ShieldAlert, CheckCircle2, TrendingUp, Layers } from 'lucide-react';

export default function DynamicReportChart({ chartType, data, dimensions, directAnswer, headline, isOutOfDomain }) {
  if (isOutOfDomain) {
    return (
      <div className="bg-[#181a24] border border-amber-500/30 rounded-2xl p-6 text-slate-300 space-y-4">
        <div className="flex items-center gap-2.5 text-amber-400 font-bold text-sm">
          <ShieldAlert className="w-5 h-5" />
          <span>Información Fuera de Dominio (Sin Alucinaciones)</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Esta consulta hace referencia a conceptos no presentes en el Lakehouse. Para garantizar máxima precisión matemática y cero alucinaciones, el motor bloquea la generación de datos artificiales.
        </p>
        <div className="p-3.5 bg-[#12141d] rounded-xl border border-[#232635] text-xs">
          <span className="text-purple-400 font-semibold block mb-1">Dimensiones Disponibles en la Base de Datos:</span>
          <span className="text-slate-400">
            Sectores Tech (Cloud, IA, Ciberseguridad, Data, SaaS), Regiones (Norteamérica, Europa, LATAM, APAC), Canales Comerciales, Calendario 2025-2026.
          </span>
        </div>
      </div>
    );
  }

  if (chartType === 'point_spotlight' && directAnswer) {
    return (
      <div className="bg-gradient-to-br from-[#1a1c27] via-[#151720] to-[#1e172a] border border-purple-500/30 rounded-2xl p-6 text-white space-y-3 relative overflow-hidden">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4" />
            Cifra Concreta Identificada
          </span>
          <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
            Precisión Exacta 100%
          </span>
        </div>
        <div className="text-4xl font-extrabold font-mono tracking-tight text-white bg-gradient-to-r from-white via-purple-100 to-pink-200 bg-clip-text text-transparent">
          {directAnswer}
        </div>
        <p className="text-xs text-slate-400">
          {headline}
        </p>
      </div>
    );
  }

  if (!data || data.length === 0) return null;

  // Prepare chart data
  const mainDim = dimensions && dimensions.length > 0 ? dimensions[dimensions.length - 1] : Object.keys(data[0])[0];
  const chartData = data.map((d, i) => ({
    name: String(d[mainDim] || `Item ${i + 1}`),
    revenue: d.total_revenue || 0,
    profit: d.total_profit || 0,
    margin_pct: d.margin_pct || 0,
  }));

  const colors = ['#9333ea', '#a855f7', '#c084fc', '#ec4899', '#f472b6', '#818cf8'];

  if (chartType === 'time_series') {
    return (
      <div className="bg-[#181a24] border border-[#232635] rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-semibold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-purple-400" />
              Evolución Temporal de la Consulta
            </h4>
            <p className="text-xs text-slate-400">Comportamiento secuencial por período</p>
          </div>
        </div>
        <div className="h-60 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="dynPurple" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a855f7" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#a855f7" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#222533" vertical={false} />
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `$${(v / 1e6).toFixed(1)}M`} tickLine={false} axisLine={false} width={65} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#191b24', borderColor: '#2e3245', borderRadius: '12px', color: '#fff', fontSize: '12px' }} 
                formatter={(val) => [`$${Number(val).toLocaleString()}`, 'Facturación']}
              />
              <Area type="monotone" dataKey="revenue" stroke="#a855f7" strokeWidth={3} fill="url(#dynPurple)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  // Default / Ranking / Comparison: Bar chart
  return (
    <div className="bg-[#181a24] border border-[#232635] rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-semibold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-pink-400" />
            Desglose Comparativo de la Consulta
          </h4>
          <p className="text-xs text-slate-400">Distribución de valores entre los segmentos consultados</p>
        </div>
      </div>
      <div className="h-60 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData.slice(0, 8)} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222533" vertical={false} />
            <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} />
            <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `$${(v / 1e6).toFixed(0)}M`} tickLine={false} axisLine={false} width={60} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#191b24', borderColor: '#2e3245', borderRadius: '12px', color: '#fff', fontSize: '12px' }} 
              formatter={(val) => [`$${Number(val).toLocaleString()}`, 'Facturación']}
            />
            <Bar dataKey="revenue" radius={[6, 6, 0, 0]}>
              {chartData.map((_, idx) => (
                <Cell key={`cell-${idx}`} fill={colors[idx % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
