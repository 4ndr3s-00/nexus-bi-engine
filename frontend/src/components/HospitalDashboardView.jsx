import React from 'react';
import { 
  Activity, 
  Bed, 
  FileSpreadsheet, 
  CalendarClock, 
  AlertCircle, 
  CheckCircle2, 
  ArrowUpRight, 
  Building, 
  Clock, 
  Sparkles,
  Zap,
  TrendingUp,
  HeartPulse,
  Users
} from 'lucide-react';
import KPICard from './KPICard';

export default function HospitalDashboardView({ hospitalData, onRunQuery, isLoading }) {
  if (!hospitalData) {
    return (
      <div className="flex-1 flex items-center justify-center p-12 text-slate-400">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mr-3"></div>
        <span>Cargando datos clínicos de la Red de 8 EPS/IPS...</span>
      </div>
    );
  }

  const {
    kpis,
    triage_by_level,
    bed_occupancy_by_ips,
    glosas_by_eps,
    appointment_opportunity,
    network_summary,
    query_latency_ms
  } = hospitalData;

  const manchesterColors = {
    1: { bg: 'bg-rose-500/20', text: 'text-rose-400', border: 'border-rose-500/40', name: 'Nivel I - Resucitación' },
    2: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/40', name: 'Nivel II - Emergencia' },
    3: { bg: 'bg-amber-500/20', text: 'text-amber-400', border: 'border-amber-500/40', name: 'Nivel III - Urgencia' },
    4: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500/40', name: 'Nivel IV - Menor' },
    5: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/40', name: 'Nivel V - No Urgente' },
  };

  const sampleClinicalQuestions = [
    "¿Cuál es el tiempo de espera promedio en Triage en los hospitales 24 horas?",
    "Ocupación de camas UCI por sede hospitalaria",
    "¿Qué EPS tiene mayor valor de glosas objetadas?",
    "Oportunidad de citas en cardiología",
    "Cuáles son los diagnósticos CIE-10 más frecuentes en urgencias"
  ];

  return (
    <div className="flex-1 flex flex-col p-6 space-y-6 bg-[#0d0e12] overflow-y-auto">
      {/* Top Banner: Network Status */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-gradient-to-r from-purple-900/20 via-[#161822] to-indigo-900/20 border border-purple-500/20 rounded-2xl p-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-purple-500/20 border border-purple-500/30 text-purple-300">
            <HeartPulse className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              Red Hospitalaria Integrada: 8 EPS / IPS
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Operación 24/7 Activa
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Monitoreo analítico asistencial de alta complejidad: Triage, Censo de Camas, Glosas RIPS y Oportunidad de Atención.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="text-right">
            <span className="text-slate-500 block text-[10px]">Tiempo de Respuesta</span>
            <span className="font-bold text-emerald-400">{query_latency_ms} ms</span>
          </div>
          <div className="w-px h-8 bg-slate-700"></div>
          <div className="text-right">
            <span className="text-slate-500 block text-[10px]">Sedes 24H</span>
            <span className="font-bold text-purple-300">4 de 8 Sedes</span>
          </div>
        </div>
      </div>

      {/* 4 Executive KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => (
          <KPICard
            key={idx}
            label={kpi.label}
            value={kpi.value}
            change={kpi.change}
            trend={kpi.trend}
          />
        ))}
      </div>

      {/* Quick AI Clinical Question Chips */}
      <div className="bg-[#12141c] border border-[#222533] rounded-2xl p-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 mb-2.5">
          <Sparkles className="w-3.5 h-3.5 text-purple-400" />
          <span>Consultas Clínicas Rápidas en Lenguaje Natural:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {sampleClinicalQuestions.map((q, i) => (
            <button
              key={i}
              onClick={() => onRunQuery(q)}
              disabled={isLoading}
              className="text-xs bg-[#161822] hover:bg-purple-900/30 hover:border-purple-500/50 text-slate-300 hover:text-white px-3 py-1.5 rounded-xl border border-[#2d3145] transition-all flex items-center gap-1.5 disabled:opacity-50"
            >
              <span>{q}</span>
              <ArrowUpRight className="w-3 h-3 text-purple-400" />
            </button>
          ))}
        </div>
      </div>

      {/* Grid: Triage Manchester & Bed Occupancy */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Triage Manchester Distribution */}
        <div className="lg:col-span-6 bg-[#12141c] border border-[#222533] rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#222533]">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-bold text-white">Triage Manchester: Tiempos de Espera & Reingresos</h3>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Urgencias 24 Horas</span>
          </div>

          <div className="space-y-3">
            {triage_by_level.map((t) => {
              const meta = manchesterColors[t.triage_level] || manchesterColors[3];
              return (
                <div key={t.triage_level} className="bg-[#161822] p-3 rounded-xl border border-[#2d3145] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${meta.bg} ${meta.text} border ${meta.border}`}>
                      {meta.name}
                    </span>
                    <span className="text-xs font-bold font-mono text-white">
                      {t.espera_promedio_min} min de espera
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 pt-1 text-[11px] text-slate-400">
                    <div>
                      <span className="text-[10px] text-slate-500 block">Atenciones</span>
                      <span className="font-semibold text-slate-200">{t.atenciones.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 block">Estancia Promedio</span>
                      <span className="font-semibold text-slate-200">{t.estancia_promedio_horas} horas</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 block">Reingreso a 72h</span>
                      <span className={`font-semibold ${t.tasa_reingreso_pct > 8 ? 'text-amber-400' : 'text-emerald-400'}`}>
                        {t.tasa_reingreso_pct}%
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Hospital Bed Occupancy by IPS */}
        <div className="lg:col-span-6 bg-[#12141c] border border-[#222533] rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#222533]">
            <div className="flex items-center gap-2">
              <Bed className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-bold text-white">Censo & Saturación de Camas por Sede IPS</h3>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Red 8 IPS</span>
          </div>

          <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
            {bed_occupancy_by_ips.map((ips, idx) => (
              <div key={idx} className="bg-[#161822] p-3 rounded-xl border border-[#2d3145] space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-200">{ips.nombre_ips}</span>
                    {ips.es_24h && (
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        24H
                      </span>
                    )}
                  </div>
                  <span className={`text-xs font-bold font-mono ${
                    ips.ocupacion_promedio_pct >= 90 ? 'text-rose-400' :
                    ips.ocupacion_promedio_pct >= 80 ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    {ips.ocupacion_promedio_pct}% Ocupación
                  </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      ips.ocupacion_promedio_pct >= 90 ? 'bg-rose-500' :
                      ips.ocupacion_promedio_pct >= 80 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, ips.ocupacion_promedio_pct)}%` }}
                  />
                </div>

                <div className="flex justify-between text-[11px] text-slate-400">
                  <span>{ips.ciudad}</span>
                  <span className="font-mono">{ips.camas_ocupadas.toLocaleString()} / {ips.camas_instaladas.toLocaleString()} camas</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Grid: Glosas by EPS & Appointment Access */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Glosas by EPS */}
        <div className="lg:col-span-6 bg-[#12141c] border border-[#222533] rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#222533]">
            <div className="flex items-center gap-2">
              <FileSpreadsheet className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-bold text-white">Auditoría RIPS: Glosas por Aseguradora EPS</h3>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Valores en COP</span>
          </div>

          <div className="space-y-2.5 max-h-[320px] overflow-y-auto pr-1">
            {glosas_by_eps.map((eps, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-[#161822] rounded-xl border border-[#2d3145]">
                <div>
                  <span className="text-xs font-bold text-slate-200 block">{eps.nombre_eps}</span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    Radicado: ${(eps.total_radicado / 1000000).toFixed(1)}M COP
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold font-mono text-rose-400 block">
                    ${(eps.total_glosado / 1000000).toFixed(1)}M COP
                  </span>
                  <span className="text-[10px] text-slate-400">Tasa: {eps.tasa_glosa_pct}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Appointment Access Times */}
        <div className="lg:col-span-6 bg-[#12141c] border border-[#222533] rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#222533]">
            <div className="flex items-center gap-2">
              <CalendarClock className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-bold text-white">Oportunidad de Citas Médicas por Especialidad</h3>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Normativa Supersalud</span>
          </div>

          <div className="space-y-2.5 max-h-[320px] overflow-y-auto pr-1">
            {appointment_opportunity.map((cita, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-[#161822] rounded-xl border border-[#2d3145]">
                <div>
                  <span className="text-xs font-bold text-slate-200 block">{cita.especialidad}</span>
                  <span className="text-[10px] text-slate-500">
                    {cita.total_citas.toLocaleString()} citas programadas
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold font-mono text-purple-300 block">
                    {cita.dias_oportunidad_promedio} días
                  </span>
                  <span className={`text-[10px] font-semibold ${
                    cita.cumplimiento_meta_pct >= 90 ? 'text-emerald-400' : 'text-amber-400'
                  }`}>
                    {cita.cumplimiento_meta_pct}% Cumplimiento
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
