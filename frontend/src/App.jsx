import React, { useState } from 'react';
import { 
  Layers, 
  BarChart3, 
  Database, 
  Sparkles, 
  Search, 
  TrendingUp, 
  Clock, 
  ShieldCheck, 
  SlidersHorizontal,
  ArrowUpRight,
  ChevronRight,
  RefreshCw,
  FileText
} from 'lucide-react';

export default function App() {
  const [query, setQuery] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="flex min-h-screen bg-[#0d0e12] text-slate-100 antialiased">
      {/* Sidebar - Inspired by reference image */}
      <aside className="w-64 border-r border-[#222533] bg-[#11131a] flex flex-col justify-between p-5 select-none">
        <div>
          {/* Logo Brand */}
          <div className="flex items-center gap-3 px-2 py-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-pink-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-900/30">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                Nexus BI
              </h1>
              <p className="text-[11px] font-medium text-purple-400 tracking-wider uppercase">
                Lakehouse Engine
              </p>
            </div>
          </div>

          {/* Nav links */}
          <nav className="space-y-1.5">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
              { id: 'analytics', label: 'AI Analytics', icon: Sparkles },
              { id: 'lakehouse', label: 'Medallion Lakehouse', icon: Database },
              { id: 'reports', label: 'Executive Reports', icon: FileText },
            ].map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-[#1e202c] text-white border border-[#2d3145] shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-[#161822]'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-purple-400' : 'text-slate-400'}`} />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Engine status pill at bottom */}
        <div className="rounded-2xl border border-[#222533] bg-[#151720] p-4 text-xs">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400">OLAP Vector Engine</span>
            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              DuckDB Ready
            </span>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed">
            Millones de registros en memoria con latencia sub-100ms.
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-20 border-b border-[#222533] px-8 flex items-center justify-between gap-6 bg-[#0d0e12]/80 backdrop-blur-md sticky top-0 z-20">
          {/* AI Search & Natural Language Query Bar */}
          <div className="flex-1 max-w-2xl relative">
            <div className="relative flex items-center">
              <Search className="w-4 h-4 text-slate-400 absolute left-4 pointer-events-none" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Pregunta a la data (ej: 'Ventas y margen neto del Q3 por categoría')..."
                className="w-full bg-[#151720] border border-[#232635] text-sm text-slate-100 placeholder-slate-500 rounded-2xl pl-11 pr-32 py-2.5 focus:outline-none focus:border-purple-500/60 focus:ring-1 focus:ring-purple-500/50 transition-all"
              />
              <button className="absolute right-1.5 px-4 py-1.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-purple-900/30 transition-all">
                <Sparkles className="w-3.5 h-3.5" />
                <span>AI Query</span>
              </button>
            </div>
          </div>

          {/* Quick Header Actions */}
          <div className="flex items-center gap-3">
            <button className="p-2.5 rounded-xl border border-[#232635] bg-[#151720] text-slate-300 hover:text-white hover:bg-[#1a1d29] transition-all">
              <SlidersHorizontal className="w-4 h-4" />
            </button>
            <div className="h-6 w-px bg-[#232635]"></div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#151720] border border-[#232635] text-xs font-mono text-purple-300">
              <Clock className="w-3.5 h-3.5 text-purple-400" />
              <span>Query Latency: 42ms</span>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="p-8 space-y-7 max-w-7xl">
          {/* KPI Cards Row (Inspired by reference UI) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              {
                title: 'Total Facturado',
                value: '$14,892,430',
                change: '+14.8%',
                subtext: 'Acumulado año en curso',
                color: 'purple',
              },
              {
                title: 'Margen Bruto Promedio',
                value: '38.4%',
                change: '+4.2%',
                subtext: 'Calculado en capa Gold',
                color: 'pink',
              },
              {
                title: 'Registros Procesados',
                value: '2,500,000',
                change: '+100%',
                subtext: 'Bronze → Silver → Gold',
                color: 'green',
              },
              {
                title: 'Tiempo de Respuesta',
                value: '38 ms',
                change: '-18%',
                subtext: 'Vectorizado con DuckDB',
                color: 'indigo',
              },
            ].map((kpi, idx) => (
              <div
                key={idx}
                className="bg-[#151720] border border-[#232635] rounded-2xl p-5 hover:border-[#2f3348] transition-all relative overflow-hidden group shadow-sm"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="text-xs font-medium text-slate-400">{kpi.title}</span>
                  <span className="inline-flex items-center gap-0.5 text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    <ArrowUpRight className="w-3 h-3" />
                    {kpi.change}
                  </span>
                </div>
                <div className="text-2xl font-bold tracking-tight text-white mb-1.5 font-mono">
                  {kpi.value}
                </div>
                <div className="text-[11px] text-slate-500">{kpi.subtext}</div>
              </div>
            ))}
          </div>

          {/* Analytics & BI Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Interactive Chart */}
            <div className="lg:col-span-2 bg-[#151720] border border-[#232635] rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="font-semibold text-base text-white">Tendencias de Rendimiento Analítico</h3>
                  <p className="text-xs text-slate-400">Ingresos netos vs. Costos por período</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400 bg-[#1c1f2b] px-3 py-1.5 rounded-lg border border-[#282c3f]">
                    Últimos 12 meses
                  </span>
                </div>
              </div>

              {/* Chart Visual Simulation */}
              <div className="h-64 flex items-end justify-between gap-3 px-2 pt-8">
                {[45, 62, 58, 75, 90, 82, 95, 110, 105, 130, 125, 142].map((val, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center gap-2 group">
                    <div 
                      className="w-full bg-gradient-to-t from-purple-900/60 via-purple-600 to-pink-500 rounded-t-lg transition-all duration-300 group-hover:brightness-125"
                      style={{ height: `${(val / 150) * 100}%` }}
                    ></div>
                    <span className="text-[10px] text-slate-500 font-mono">M{i + 1}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Medallion Architecture Monitor */}
            <div className="bg-[#151720] border border-[#232635] rounded-2xl p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-base text-white">Arquitectura Medallón</h3>
                  <span className="text-[11px] text-purple-400 bg-purple-950/40 border border-purple-800/40 px-2 py-0.5 rounded-full">
                    En Vivo
                  </span>
                </div>
                <p className="text-xs text-slate-400 mb-6">
                  Flujo de transformación desde ingesta raw hasta el modelo dimensional.
                </p>

                <div className="space-y-4">
                  <div className="p-3 rounded-xl bg-[#1a1d28] border border-[#282c3f] flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 text-xs font-bold">
                        B
                      </div>
                      <div>
                        <div className="text-xs font-medium text-white">Bronze (Raw Events)</div>
                        <div className="text-[10px] text-slate-400">JSONL Ingestión continua</div>
                      </div>
                    </div>
                    <span className="text-xs font-mono text-slate-300">2.5M rows</span>
                  </div>

                  <div className="p-3 rounded-xl bg-[#1a1d28] border border-[#282c3f] flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-slate-300/10 border border-slate-300/30 flex items-center justify-center text-slate-300 text-xs font-bold">
                        S
                      </div>
                      <div>
                        <div className="text-xs font-medium text-white">Silver (Conformed)</div>
                        <div className="text-[10px] text-slate-400">Parquet columnar limpio</div>
                      </div>
                    </div>
                    <span className="text-xs font-mono text-slate-300">2.5M rows</span>
                  </div>

                  <div className="p-3 rounded-xl bg-[#1a1d28] border border-purple-500/30 bg-purple-950/10 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-300 text-xs font-bold">
                        G
                      </div>
                      <div>
                        <div className="text-xs font-medium text-white">Gold (Kimball Star)</div>
                        <div className="text-[10px] text-purple-300">Fact & Dimension Tables</div>
                      </div>
                    </div>
                    <span className="text-xs font-mono text-purple-300 font-bold">DuckDB</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-[#232635] mt-6 flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1.5 text-emerald-400">
                  <ShieldCheck className="w-4 h-4" />
                  Constraints verificados
                </span>
                <span className="font-mono">100% Determinista</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
