import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import KPICard from './components/KPICard';
import TrendChart from './components/TrendChart';
import CategoryChart from './components/CategoryChart';
import ExecutiveReportView from './components/ExecutiveReportView';
import LakehouseMonitor from './components/LakehouseMonitor';

export default function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  
  // Dashboard state
  const [overview, setOverview] = useState(null);
  const [activeReport, setActiveReport] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  // Load initial dashboard overview on mount
  const fetchOverview = async () => {
    try {
      const res = await fetch('/api/v1/dashboard/overview');
      if (res.ok) {
        const data = await res.json();
        setOverview(data);
      }
    } catch (err) {
      console.error('Failed to load overview data:', err);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  // Handle Natural Language AI Query
  const handleRunQuery = async (searchQuery) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/v1/report/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: searchQuery })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Error procesando la consulta');
      }
      const reportData = await res.json();
      setActiveReport(reportData);
      setActiveSection('ai-report');
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Seed 1M Records
  const handleSeedData = async () => {
    setIsSeeding(true);
    try {
      const res = await fetch('/api/v1/lakehouse/seed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ n_rows: 1000000 })
      });
      if (res.ok) {
        await fetchOverview();
      }
    } catch (err) {
      console.error('Seeding error:', err);
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#0d0e12] text-slate-100 antialiased font-sans">
      {/* Left Sidebar */}
      <Sidebar 
        activeSection={activeSection} 
        setActiveSection={setActiveSection}
        onSeedData={handleSeedData}
        isSeeding={isSeeding}
        lakehouseStats={overview?.lakehouse_stats}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top Header with AI Query Bar & Real-time Latency */}
        <Header 
          query={query}
          setQuery={setQuery}
          onRunQuery={handleRunQuery}
          isLoading={isLoading}
          latencyMs={activeReport?.latency_ms || overview?.query_latency_ms}
          onRefresh={fetchOverview}
          onSelectSuggestion={(s) => {
            setQuery(s);
            handleRunQuery(s);
          }}
        />

        {/* Dynamic Body Content */}
        <div className="p-8 space-y-8 max-w-7xl w-full mx-auto">
          {errorMsg && (
            <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
              <span>{errorMsg}</span>
              <button onClick={() => setErrorMsg(null)} className="text-rose-400 hover:text-white font-bold ml-4">✕</button>
            </div>
          )}

          {/* AI Executive Report View (When active) */}
          {activeSection === 'ai-report' && activeReport && (
            <ExecutiveReportView 
              report={activeReport} 
              onClose={() => setActiveSection('dashboard')} 
            />
          )}

          {/* Medallion Lakehouse View */}
          {activeSection === 'lakehouse' && (
            <LakehouseMonitor stats={overview?.lakehouse_stats} />
          )}

          {/* General Executive Dashboard View */}
          {activeSection === 'dashboard' && (
            <>
              {/* Row of 4 KPI Cards - Inspired directly by reference UI */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                {overview?.kpis?.map((kpi, idx) => (
                  <KPICard
                    key={idx}
                    label={kpi.label}
                    value={kpi.value}
                    change={kpi.change}
                    trend={kpi.trend}
                    subtext={
                      idx === 0 ? 'Facturación total acumulada' :
                      idx === 1 ? 'Margen calculado en capa Gold' :
                      idx === 2 ? 'Transacciones en Lakehouse' :
                      'Cómputo en memoria con DuckDB'
                    }
                  />
                ))}
              </div>

              {/* Main Charts Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <TrendChart data={overview?.monthly_trend} />
                <CategoryChart data={overview?.category_breakdown} />
              </div>

              {/* In-page Medallion Monitor for single-page unified fluid experience */}
              <LakehouseMonitor stats={overview?.lakehouse_stats} />
            </>
          )}
        </div>
      </main>
    </div>
  );
}
