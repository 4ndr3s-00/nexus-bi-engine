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
import { Sparkles, ShieldAlert, CheckCircle2, TrendingUp, Layers, Clock, Activity, Users } from 'lucide-react';

export default function DynamicReportChart({ chartType, data, dimensions, directAnswer, headline, isOutOfDomain }) {
  if (isOutOfDomain) {
    return (
      <div className="bg-[#181a24] border border-amber-500/30 rounded-2xl p-6 text-slate-300 space-y-4">
        <div className="flex items-center gap-2.5 text-amber-400 font-bold text-sm">
          <ShieldAlert className="w-5 h-5" />
          <span>Información Fuera de Dominio (Sin Alucinaciones)</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Esta consulta no corresponde a la red de 8 EPS/IPS ni al modelo analítico. Para garantizar máxima precisión clínica y cero alucinaciones, el sistema bloquea datos inventados.
        </p>
        <div className="p-3.5 bg-[#12141d] rounded-xl border border-[#232635] text-xs">
          <span className="text-purple-400 font-semibold block mb-1">Dimensiones Clínicas Disponibles:</span>
          <span className="text-slate-400">
            Urgencias Triage Manchester I-V, Censo de Camas UCI, Auditoría de Glosas RIPS, Oportunidad de Citas por Especialidad y Sedes 24 Horas.
          </span>
        </div>
      </div>
    );
  }

  // 1. Point Spotlight Card for specific single answer queries
  if (chartType === 'point_spotlight' && directAnswer) {
    const row = data && data.length > 0 ? data[0] : null;
    return (
      <div className="bg-gradient-to-br from-[#1a1c27] via-[#151720] to-[#1e172a] border border-purple-500/30 rounded-2xl p-6 text-white space-y-4 relative overflow-hidden shadow-xl">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-purple-400" />
            Cifra Concreta Verificada en Lakehouse
          </span>
          <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            Precisión Matemática 100%
          </span>
        </div>

        <div>
          <div className="text-4xl font-extrabold font-mono tracking-tight text-white bg-gradient-to-r from-white via-purple-100 to-pink-200 bg-clip-text text-transparent">
            {directAnswer}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {headline}
          </p>
        </div>

        {/* Breakdown chips if clinical row exists */}
        {row && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 pt-2 border-t border-[#232635]">
            {row.estancia_promedio_horas !== undefined && (
              <div className="bg-[#141620] p-2.5 rounded-xl border border-[#2d3145]">
                <span className="text-[10px] text-slate-500 block uppercase font-semibold">Media Estancia</span>
                <span className="text-xs font-mono font-bold text-purple-300">{row.estancia_promedio_horas} horas</span>
              </div>
            )}
            {row.tiempo_espera_promedio_min !== undefined && (
              <div className="bg-[#141620] p-2.5 rounded-xl border border-[#2d3145]">
                <span className="text-[10px] text-slate-500 block uppercase font-semibold">Espera Triage</span>
                <span className="text-xs font-mono font-bold text-amber-300">{row.tiempo_espera_promedio_min} min</span>
              </div>
            )}
            {row.total_atenciones !== undefined && (
              <div className="bg-[#141620] p-2.5 rounded-xl border border-[#2d3145]">
                <span className="text-[10px] text-slate-500 block uppercase font-semibold">Atenciones</span>
                <span className="text-xs font-mono font-bold text-emerald-300">{Number(row.total_atenciones).toLocaleString()}</span>
              </div>
            )}
            {row.tasa_reingreso_pct !== undefined && (
              <div className="bg-[#141620] p-2.5 rounded-xl border border-[#2d3145]">
                <span className="text-[10px] text-slate-500 block uppercase font-semibold">Reingreso 72h</span>
                <span className="text-xs font-mono font-bold text-cyan-300">{row.tasa_reingreso_pct}%</span>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  if (!data || data.length === 0) return null;

  // 2. Multi-row Dynamic Metrics Detection
  const priorityMetrics = [
    { key: 'estancia_promedio_horas', label: 'Estancia Media (horas)', unit: 'h' },
    { key: 'tiempo_espera_promedio_min', label: 'Espera Triage (min)', unit: 'min' },
    { key: 'tasa_ocupacion_pct', label: 'Ocupación (%)', unit: '%' },
    { key: 'total_glosado', label: 'Valor Glosado (COP)', unit: '$' },
    { key: 'oportunidad_promedio_dias', label: 'Oportunidad Citas (días)', unit: 'días' },
    { key: 'total_atenciones', label: 'Atenciones Urgencias', unit: 'pacientes' },
    { key: 'total_revenue', label: 'Facturación ($)', unit: '$' },
    { key: 'total_profit', label: 'Margen ($)', unit: '$' }
  ];

  let activeMetric = priorityMetrics.find(m => data[0] && data[0][m.key] !== undefined && data[0][m.key] !== null) || {
    key: 'value', label: 'Valor Analítico', unit: ''
  };

  const mainDim = dimensions && dimensions.length > 0 ? dimensions[0] : Object.keys(data[0])[0];
  
  const chartData = data.map((d, i) => {
    const rawVal = Number(d[activeMetric.key] || 0);
    return {
      name: String(d[mainDim] || `Item ${i + 1}`),
      value: rawVal,
      displayValue: activeMetric.unit === '$' 
        ? `$${(rawVal / 1e6).toFixed(1)}M` 
        : `${rawVal} ${activeMetric.unit}`
    };
  });

  const colors = ['#9333ea', '#a855f7', '#c084fc', '#ec4899', '#f472b6', '#818cf8', '#38bdf8', '#34d399'];

  return (
    <div className="bg-[#181a24] border border-[#232635] rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-semibold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-purple-400" />
            {activeMetric.label}: Comparativa por {mainDim.replace('_', ' ')}
          </h4>
          <p className="text-xs text-slate-400">Distribución de valores cuantitativos extraídos de la capa Gold</p>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData.slice(0, 10)} margin={{ top: 5, right: 10, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222533" vertical={false} />
            <XAxis 
              dataKey="name" 
              stroke="#64748b" 
              fontSize={10} 
              tickLine={false} 
              interval={0}
              angle={-15}
              textAnchor="end"
            />
            <YAxis 
              stroke="#64748b" 
              fontSize={11} 
              tickFormatter={(v) => activeMetric.unit === '$' ? `$${(v / 1e6).toFixed(0)}M` : `${v}`} 
              tickLine={false} 
              axisLine={false} 
              width={50} 
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#191b24', borderColor: '#2e3245', borderRadius: '12px', color: '#fff', fontSize: '12px' }} 
              formatter={(val) => [
                activeMetric.unit === '$' ? `$${Number(val).toLocaleString()} COP` : `${val} ${activeMetric.unit}`, 
                activeMetric.label
              ]}
            />
            <Bar dataKey="value" radius={[6, 6, 0, 0]}>
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
