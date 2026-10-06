import React from 'react';
import { Database, ShieldCheck, HardDrive, ArrowRight, Layers } from 'lucide-react';

export default function LakehouseMonitor({ stats }) {
  const tables = stats?.tables || {};
  const totalFactRows = stats?.total_fact_rows || 0;
  const dbSizeMb = stats?.db_size_mb || 0;

  return (
    <div className="bg-[#151720] border border-[#232635] rounded-3xl p-7 space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-[#232635]">
        <div>
          <h3 className="font-bold text-lg text-white">Arquitectura Medallón del Lakehouse</h3>
          <p className="text-xs text-slate-400">Ingesta continua, limpieza columnar y modelo dimensional Kimball</p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400 bg-[#1c1f2b] px-3 py-1.5 rounded-xl border border-[#282c3f]">
          <HardDrive className="w-3.5 h-3.5 text-purple-400" />
          <span>Almacenamiento: {dbSizeMb} MB</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Bronze Card */}
        <div className="bg-[#181a24] border border-[#282b3d] rounded-2xl p-5 space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 text-xs font-bold">
              B
            </span>
            <span className="text-[10px] font-mono text-slate-400">Bronze Layer</span>
          </div>
          <div>
            <div className="text-base font-bold text-white">Raw Staging Events</div>
            <p className="text-xs text-slate-400 mt-1">Payloads semiestructurados JSONL & Parquet raw sin transformar.</p>
          </div>
          <div className="pt-3 border-t border-[#232637] flex items-center justify-between text-xs font-mono">
            <span className="text-slate-500">Volumen:</span>
            <span className="text-amber-300 font-bold">{totalFactRows.toLocaleString()} rows</span>
          </div>
        </div>

        {/* Silver Card */}
        <div className="bg-[#181a24] border border-[#282b3d] rounded-2xl p-5 space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="w-8 h-8 rounded-lg bg-slate-300/10 border border-slate-300/30 flex items-center justify-center text-slate-200 text-xs font-bold">
              S
            </span>
            <span className="text-[10px] font-mono text-slate-400">Silver Layer</span>
          </div>
          <div>
            <div className="text-base font-bold text-white">Cleaned & Conformed</div>
            <p className="text-xs text-slate-400 mt-1">Deduplicado, filtrado de anomalías y compresión ZSTD.</p>
          </div>
          <div className="pt-3 border-t border-[#232637] flex items-center justify-between text-xs font-mono">
            <span className="text-slate-500">Compresión:</span>
            <span className="text-slate-200 font-bold">Parquet Columnar</span>
          </div>
        </div>

        {/* Gold Card */}
        <div className="bg-[#181a24] border border-purple-500/40 bg-purple-950/10 rounded-2xl p-5 space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="w-8 h-8 rounded-lg bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-300 text-xs font-bold">
              G
            </span>
            <span className="text-[10px] font-mono text-purple-300">Gold Layer</span>
          </div>
          <div>
            <div className="text-base font-bold text-white">Kimball Star Schema</div>
            <p className="text-xs text-slate-300 mt-1">Tablas de Hechos y Dimensiones en DuckDB para consultas OLAP.</p>
          </div>
          <div className="pt-3 border-t border-purple-500/20 flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">Consultas:</span>
            <span className="text-purple-300 font-bold">&lt; 50ms Latencia</span>
          </div>
        </div>
      </div>

      {/* Relational Table Breakdown */}
      <div className="bg-[#181a24] border border-[#252839] rounded-2xl p-5">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
          <Layers className="w-4 h-4 text-purple-400" />
          Conteo de Tablas del Esquema Estrella (DuckDB)
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs font-mono">
          {Object.entries(tables).map(([tableName, count]) => (
            <div key={tableName} className="p-3 rounded-xl bg-[#13151e] border border-[#212433]">
              <div className="text-slate-400 text-[11px] truncate">{tableName}</div>
              <div className="text-base font-bold text-white mt-1">
                {typeof count === 'number' ? count.toLocaleString() : count}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
