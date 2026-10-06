import React from 'react';
import { ArrowUpRight, ArrowDownRight, Activity } from 'lucide-react';

export default function KPICard({ label, value, change, trend = "up", subtext }) {
  const isPositive = trend === "up" || change?.startsWith("+");

  return (
    <div className="bg-[#151720] border border-[#232635] rounded-2xl p-5 hover:border-[#2f3348] transition-all relative overflow-hidden group shadow-sm flex flex-col justify-between">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-medium text-slate-400">{label}</span>
        {change && (
          <span className={`inline-flex items-center gap-0.5 text-[11px] font-semibold px-2 py-0.5 rounded-full border ${
            isPositive
              ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
              : 'text-rose-400 bg-rose-500/10 border-rose-500/20'
          }`}>
            {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            {change}
          </span>
        )}
      </div>
      <div>
        <div className="text-2xl font-bold tracking-tight text-white mb-1 font-mono">
          {value}
        </div>
        {subtext && <div className="text-[11px] text-slate-500">{subtext}</div>}
      </div>
      
      {/* Subtle bottom glow highlight on hover */}
      <div className="absolute inset-x-0 bottom-0 h-0.5 bg-gradient-to-r from-transparent via-purple-500/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
    </div>
  );
}
