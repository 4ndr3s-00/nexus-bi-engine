import React, { useState } from 'react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  CartesianGrid 
} from 'recharts';

export default function TrendChart({ data }) {
  const [metric, setMetric] = useState('revenue');

  // Format tick numbers (e.g. 500k, 1M)
  const formatYAxis = (val) => {
    if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(1)}M`;
    if (val >= 1_000) return `$${(val / 1_000).toFixed(0)}k`;
    return val;
  };

  const chartData = (data || []).map(item => ({
    name: item.month_name?.slice(0, 3) || `M${item.month}`,
    revenue: item.revenue || 0,
    profit: item.profit || 0,
    orders: item.orders || 0,
  }));

  return (
    <div className="bg-[#151720] border border-[#232635] rounded-2xl p-6 flex flex-col justify-between">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-semibold text-base text-white">Tendencias Financieras Mensuales</h3>
          <p className="text-xs text-slate-400">Datos agregados en milisegundos desde la capa Gold</p>
        </div>
        <div className="flex items-center gap-2 bg-[#1c1f2b] p-1 rounded-xl border border-[#282c3f]">
          <button
            onClick={() => setMetric('revenue')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
              metric === 'revenue' 
                ? 'bg-purple-600 text-white shadow-sm' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Facturación
          </button>
          <button
            onClick={() => setMetric('profit')}
            className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
              metric === 'profit' 
                ? 'bg-purple-600 text-white shadow-sm' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Margen Neto
          </button>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="purpleGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#a855f7" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#a855f7" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="pinkGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ec4899" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#ec4899" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#222533" vertical={false} />
            <XAxis 
              dataKey="name" 
              stroke="#64748b" 
              fontSize={11} 
              tickLine={false} 
              axisLine={{ stroke: '#222533' }}
            />
            <YAxis 
              stroke="#64748b" 
              fontSize={11} 
              tickFormatter={formatYAxis} 
              tickLine={false} 
              axisLine={false}
              width={65}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#191b24', 
                borderColor: '#2e3245', 
                borderRadius: '12px',
                color: '#fff',
                fontSize: '12px',
                boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)'
              }} 
              formatter={(val) => [`$${Number(val).toLocaleString()}`, metric === 'revenue' ? 'Facturación' : 'Margen']}
            />
            <Area 
              type="monotone" 
              dataKey={metric} 
              stroke={metric === 'revenue' ? '#a855f7' : '#ec4899'} 
              strokeWidth={3} 
              fillOpacity={1} 
              fill={metric === 'revenue' ? 'url(#purpleGradient)' : 'url(#pinkGradient)'} 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
