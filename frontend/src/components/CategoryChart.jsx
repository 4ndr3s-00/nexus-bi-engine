import React from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Cell 
} from 'recharts';

export default function CategoryChart({ data }) {
  const chartData = (data || []).slice(0, 6).map(item => ({
    name: item.category || item.region || 'N/A',
    revenue: item.revenue || 0,
    profit: item.profit || 0,
    margin_pct: item.margin_pct || 0
  }));

  const colors = [
    '#9333ea', '#a855f7', '#c084fc', '#ec4899', '#f472b6', '#818cf8'
  ];

  return (
    <div className="bg-[#151720] border border-[#232635] rounded-2xl p-6 flex flex-col justify-between">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-base text-white">Rendimiento por Categoría</h3>
          <p className="text-xs text-slate-400">Distribución de ingresos en la capa Gold</p>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <XAxis 
              type="number" 
              stroke="#64748b" 
              fontSize={11} 
              tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`} 
              axisLine={false} 
              tickLine={false} 
            />
            <YAxis 
              dataKey="name" 
              type="category" 
              stroke="#94a3b8" 
              fontSize={11} 
              axisLine={false} 
              tickLine={false} 
              width={125}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#191b24', 
                borderColor: '#2e3245', 
                borderRadius: '12px',
                color: '#fff',
                fontSize: '12px'
              }} 
              formatter={(val) => [`$${Number(val).toLocaleString()}`, 'Facturación']}
            />
            <Bar dataKey="revenue" radius={[0, 8, 8, 0]}>
              {chartData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
