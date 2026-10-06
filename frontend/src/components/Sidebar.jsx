import React from 'react';
import { 
  BarChart3, 
  Sparkles, 
  Database, 
  FileText, 
  Layers, 
  Zap,
  CheckCircle2,
  Cpu
} from 'lucide-react';

export default function Sidebar({ activeSection, setActiveSection, onSeedData, isSeeding, lakehouseStats }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard General', icon: BarChart3 },
    { id: 'ai-report', label: 'AI Executive Report', icon: Sparkles },
    { id: 'lakehouse', label: 'Medallion Lakehouse', icon: Database },
  ];

  return (
    <aside className="w-64 border-r border-[#222533] bg-[#11131a] flex flex-col justify-between p-5 select-none shrink-0 min-h-screen">
      <div>
        {/* Brand Logo - Inspired by reference UI */}
        <div className="flex items-center gap-3 px-2 py-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-pink-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-900/30">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              Nexus BI
            </h1>
            <p className="text-[10px] font-semibold text-purple-400 tracking-wider uppercase">
              Lakehouse Analytics
            </p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-[#1e202c] text-white border border-[#2d3145] shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-[#161822]'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-purple-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Quick Seeding Trigger */}
        <div className="mt-8 pt-6 border-t border-[#222533]">
          <div className="text-xs font-semibold uppercase text-slate-500 tracking-wider mb-3 px-2">
            Ingesta Rápida
          </div>
          <button
            onClick={onSeedData}
            disabled={isSeeding}
            className="w-full flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-purple-600/20 to-pink-600/20 hover:from-purple-600/30 hover:to-pink-600/30 text-purple-300 border border-purple-500/30 transition-all disabled:opacity-50"
          >
            <Zap className={`w-3.5 h-3.5 text-purple-400 ${isSeeding ? 'animate-spin' : ''}`} />
            <span>{isSeeding ? 'Ingestando 1M Filas...' : 'Cargar +1M Registros'}</span>
          </button>
        </div>
      </div>

      {/* Engine Status Pill */}
      <div className="rounded-2xl border border-[#222533] bg-[#151720] p-4 text-xs">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-slate-400 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-purple-400" />
            DuckDB OLAP
          </span>
          <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            En Memoria
          </span>
        </div>
        <p className="text-[11px] text-slate-500 leading-relaxed font-mono">
          {lakehouseStats?.total_fact_rows ? `${lakehouseStats.total_fact_rows.toLocaleString()} filas activas` : '1,000,000+ filas'}
        </p>
      </div>
    </aside>
  );
}
