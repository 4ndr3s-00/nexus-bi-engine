import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import HospitalDashboardView from './components/HospitalDashboardView';
import DocumentAuditorView from './components/DocumentAuditorView';
import ExecutiveReportView from './components/ExecutiveReportView';

export default function App() {
  const [activeSection, setActiveSection] = useState('hospital-bi');
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  
  // Hospital and BI state
  const [hospitalOverview, setHospitalOverview] = useState(null);
  const [activeReport, setActiveReport] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  // Load initial hospital overview on mount
  const fetchHospitalOverview = async () => {
    try {
      const res = await fetch('/api/v1/hospital/overview');
      if (res.ok) {
        const data = await res.json();
        setHospitalOverview(data);
      }
    } catch (err) {
      console.error('Failed to load hospital overview data:', err);
    }
  };

  useEffect(() => {
    fetchHospitalOverview();
  }, []);

  // Handle Natural Language Clinical AI Query
  const handleRunQuery = async (searchQuery) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/v1/hospital/report', {
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

  // Handle Seed Clinical Lakehouse Data
  const handleSeedData = async () => {
    setIsSeeding(true);
    try {
      const res = await fetch('/api/v1/lakehouse/seed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ n_rows: 400000 })
      });
      if (res.ok) {
        await fetchHospitalOverview();
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
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top Header with Clinical AI Query Bar & Real-time Latency */}
        <Header 
          query={query}
          setQuery={setQuery}
          onRunQuery={handleRunQuery}
          isLoading={isLoading}
          latencyMs={activeReport?.latency_ms || hospitalOverview?.query_latency_ms}
          onRefresh={() => {
            fetchHospitalOverview();
          }}
          onSelectSuggestion={(s) => {
            setQuery(s);
            handleRunQuery(s);
          }}
        />

        {/* Global Error Banner */}
        {errorMsg && (
          <div className="mx-8 mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center justify-between">
            <span>{errorMsg}</span>
            <button onClick={() => setErrorMsg(null)} className="underline ml-4">Cerrar</button>
          </div>
        )}

        {/* Section View Routing */}
        <div className="flex-1 flex flex-col min-w-0">
          {activeSection === 'hospital-bi' && (
            <HospitalDashboardView 
              hospitalData={hospitalOverview} 
              onRunQuery={handleRunQuery}
              isLoading={isLoading}
            />
          )}

          {activeSection === 'strata-auditor' && (
            <DocumentAuditorView 
              onRefreshOverview={fetchHospitalOverview} 
            />
          )}

          {activeSection === 'ai-report' && (
            <ExecutiveReportView 
              report={activeReport}
              onBack={() => setActiveSection('hospital-bi')}
              onExportHtml={async () => {
                const res = await fetch('/api/v1/report/export-html', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ question: activeReport?.question || '' })
                });
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Informe_Clinico_Nexus_BI.html`;
                a.click();
              }}
            />
          )}
        </div>
      </main>
    </div>
  );
}
